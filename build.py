#!/usr/bin/env python
"""Script + slide deck -> rehearsal audio + practice app (Kokoro-82M, local, CPU).

  python build.py --script talks/NAME/script.md --deck talks/NAME/deck.pdf --out talks/NAME/app
  python build.py ... --voice af_bella --speed 1.0
  python build.py ... --no-images     skip re-rendering slide images (no --deck needed)

Every sentence clip is cached in cache/ by (text, voice, speed), so after an edit to
the script only the changed sentences are synthesized again.
The script and the deck never leave this computer.
"""
import argparse
import hashlib
import json
import os
import re
import warnings
from pathlib import Path

THREADS = int(os.environ.get("VOICE_THREADS", "8"))
os.environ.setdefault("OMP_NUM_THREADS", str(THREADS))
warnings.filterwarnings("ignore")
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
TSV = HERE / "pronunciation.tsv"
CACHE = HERE / "cache"
MODELS = HERE / "models"
TEMPLATE = HERE / "app" / "index.html"
SR = 24000
PAUSE_SENT, PAUSE_PARA = 0.4, 0.7
NBSP = " "


# ---------------------------------------------------------------- script
def split_sentences(par):
    par = re.sub(r"\b(Dr|Mr|Ms|Prof)\. ", r"\1." + NBSP, par.strip())  # keep "Dr. Lee" together
    out = [s.strip() for s in re.split(r"(?<=[.?!])\s+", par) if s.strip()]
    return [s.replace(NBSP, " ") for s in out]


def load_script(path):
    slides, cur = [], None
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^## Slide (\d+)\.\s*(.*?)\s*(?:\((\d+):(\d\d)\))?\s*$", line)
        if m:
            cur = {"n": int(m.group(1)), "title": m.group(2),
                   "target": int(m.group(3)) * 60 + int(m.group(4)) if m.group(3) else 0,
                   "pars": [], "note": ""}
            slides.append(cur)
        elif cur is None or not line.strip() or line.startswith("#"):
            continue
        elif line.strip().startswith("*") and line.strip().endswith("*"):
            cur["note"] = line.strip().strip("*")
        else:
            cur["pars"].append(line.strip())
    return slides


# ---------------------------------------------------------------- pronunciation
def load_rules():
    rules = []
    for line in TSV.read_text(encoding="utf-8").split("\n"):
        if line.strip() and not line.startswith("#"):
            c = line.split("\t")
            rules.append((c[0].strip(), c[1].strip()))
    rules.sort(key=lambda r: -len(r[0]))
    return rules


def apply_rules(sentence, rules):
    if not rules:
        return sentence
    table = dict(rules)
    pat = re.compile(r"(?<![\w-])(" + "|".join(re.escape(w) for w, _ in rules) + r")(?![\w-])")

    def spoken(m):
        word = re.sub(r"[^A-Za-z]", "", m.group(1)) or "x"
        return re.sub(r"/([^/]+)/", lambda p: f"[{word}](/{p.group(1)}/)", table[m.group(1)])
    return pat.sub(spoken, sentence)


_g2p = None


def g2p(text):
    global _g2p
    if _g2p is None:
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
        from misaki import en, espeak
        _g2p = en.G2P(trf=False, british=False, fallback=espeak.EspeakFallback(british=False))
    ph, _ = _g2p(text)
    ph = ph.strip()
    if text[-1] in ".?!" and ph and ph[-1] not in ".?!":
        ph += text[-1]
    return ph.replace("❓", "")


# ---------------------------------------------------------------- synthesis
_kokoro = None


def kokoro():
    global _kokoro
    if _kokoro is None:
        import onnxruntime as ort
        from kokoro_onnx import Kokoro
        so = ort.SessionOptions()
        so.intra_op_num_threads = THREADS
        so.inter_op_num_threads = 1
        sess = ort.InferenceSession(str(MODELS / "kokoro-v1.0.onnx"), so,
                                    providers=["CPUExecutionProvider"])
        _kokoro = Kokoro.from_session(sess, str(MODELS / "voices-v1.0.bin"))
    return _kokoro


def trim_edges(x, pad_head=0.02, pad_tail=0.06, top_db=42.0):
    win = int(0.01 * SR)
    n = len(x) // win
    rms = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
    idx = np.where(rms > rms.max() * 10 ** (-top_db / 20))[0]
    a = max(0, idx[0] * win - int(pad_head * SR))
    b = min(len(x), (idx[-1] + 1) * win + int(pad_tail * SR))
    y = x[a:b].copy()
    f = int(0.005 * SR)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    return y


def sentence_audio(s, voice, speed, rules):
    import soundfile as sf
    spoken = apply_rules(s, rules)
    key = hashlib.sha1(f"{spoken}|{voice}|{speed}".encode()).hexdigest()[:16]
    f = CACHE / f"{key}.wav"
    if f.exists():
        y, _ = sf.read(str(f), dtype="float32")
        return y, False
    audio, sr = kokoro().create(g2p(spoken), kokoro().get_voice_style(voice), speed=speed,
                                is_phonemes=True, trim=False)
    y = trim_edges(np.asarray(audio, dtype=np.float32))
    sf.write(str(f), y, SR, subtype="PCM_16")
    return y, True


def write_mp3(path, x, kbps=64):
    import lameenc
    enc = lameenc.Encoder()
    enc.set_bit_rate(kbps)
    enc.set_in_sample_rate(SR)
    enc.set_channels(1)
    enc.set_quality(2)
    x = x * (10 ** (-1 / 20) / max(1e-6, np.abs(x).max()))
    Path(path).write_bytes(enc.encode((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()) + enc.flush())


def render_images(deck, app):
    import pymupdf
    (app / "img").mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(deck))
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=110).save(str(app / "img" / f"slide_{i:02d}.png"))
    return len(doc)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Build a talk-practice app from a script and a deck PDF.")
    ap.add_argument("--script", type=Path, required=True, help="script in Markdown (see README)")
    ap.add_argument("--deck", type=Path, help="deck PDF, one page per slide (not needed with --no-images)")
    ap.add_argument("--out", type=Path, required=True, help="output folder, e.g. talks/NAME/app")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=0.85)
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    if not a.no_images and not a.deck:
        ap.error("--deck is required unless --no-images is given")
    if not (MODELS / "kokoro-v1.0.onnx").exists():
        ap.error("model files are missing; run: python get_models.py")

    app = a.out.resolve()
    CACHE.mkdir(exist_ok=True)
    (app / "audio").mkdir(parents=True, exist_ok=True)
    name = app.parent.name if app.name == "app" else app.name
    (app / "index.html").write_text(TEMPLATE.read_text(encoding="utf-8").replace(
        "<title>Talk Practice</title>", f"<title>Talk Practice: {name}</title>"), encoding="utf-8")
    rules = load_rules()
    slides = load_script(a.script)
    if not slides:
        ap.error(f"no '## Slide N. Title' headings found in {a.script}")
    if not a.no_images:
        pages = render_images(a.deck, app)
        print("slide images:", pages)
        if pages != len(slides):
            print(f"WARNING: the deck has {pages} pages but the script has {len(slides)} slides")

    data, new_total = [], 0
    for sl in slides:
        parts, sents, t = [], [], 0.0
        for pi, par in enumerate(sl["pars"]):
            ss = split_sentences(par)
            for si, s in enumerate(ss):
                y, new = sentence_audio(s, a.voice, a.speed, rules)
                new_total += new
                last_par = si == len(ss) - 1
                last = last_par and pi == len(sl["pars"]) - 1
                pause = 0.0 if last else (PAUSE_PARA if last_par else PAUSE_SENT)
                sents.append({"text": s, "start": round(t, 3), "end": round(t + len(y) / SR, 3), "par": pi})
                parts += [y, np.zeros(int(pause * SR), dtype=np.float32)]
                t += len(y) / SR + int(pause * SR) / SR
        if parts:
            write_mp3(app / "audio" / f"slide_{sl['n']:02d}.mp3", np.concatenate(parts))
        words = sum(len(s["text"].split()) for s in sents)
        data.append({"n": sl["n"], "title": sl["title"], "target": sl["target"], "note": sl["note"],
                     "dur": round(t, 2), "words": words, "sentences": sents})
        print(f"slide {sl['n']:2d}: {t:6.1f} s (target {sl['target']:4d} s), {len(sents)} sentences", flush=True)

    (app / "data.js").write_text("window.TALK = " + json.dumps(
        {"voice": a.voice, "speed": a.speed, "slides": data}, ensure_ascii=False) + ";\n", encoding="utf-8")
    main_talk = sum(s["dur"] for s in data if s["target"])
    print(f"new clips: {new_total}; main talk audio {main_talk/60:.1f} min (slides with a target time)")
    print("open:", app / "index.html")


if __name__ == "__main__":
    main()
