# Claude Code에 붙여 넣는 프롬프트

저장소를 clone한 폴더에서 Claude Code를 열고, 아래 두 줄 사이의 내용을 그대로 붙여 넣으세요.

---

I cloned talk-practice-kit into this folder. Help me build a practice page for my own English talk. Reply in the language I write in; keep file names, commands and technical terms in English.

Privacy rule, which comes before everything else: my script and my deck stay on this computer. Never send their content to any online service. That means no online TTS, no web translator, no web search that quotes my text, and no upload of any kind. Never `git add` anything inside `talks/`.

Steps:

1. Read `README.md` and `talks/README.md`.
2. Run the setup if `.venv/` or `models/` is missing: `py -3.13 setup_kit.py` on Windows, `python3.13 setup_kit.py` on macOS (3.12 also works). If no suitable Python is installed, tell me how to install one and stop there.
3. Build the example (`example/script.md`, `example/deck.pdf` to `example/app`) and ask me to open `example/app/index.html` and confirm that I hear the audio and the highlight follows it.
4. Ask me for the paths to my script and my deck PDF, and for a short name for the talk (lowercase letters, digits and hyphens).
   - If my deck is a .pptx, ask me to save it as a PDF from PowerPoint (one page per slide).
   - If my script is not in the README format (`## Slide N. Title (m:ss)` headings, one paragraph per line, blank lines between paragraphs, `*...*` for notes), convert it for me locally. Keep my wording exactly. Ask me for the target time of each slide if I have not given one. Show me anything you are unsure about, such as where one slide ends and the next begins.
5. Copy both files to `talks/<short-name>/script.md` and `talks/<short-name>/deck.pdf`. Leave my originals where they are.
6. Build: `python build.py --script talks/<short-name>/script.md --deck talks/<short-name>/deck.pdf --out talks/<short-name>/app` with the Python in `.venv`.
7. Report a table with the audio length and the target time of every slide, plus the totals. Mark the slides that run over their target. If the build warns that the page count and the slide count differ, tell me which slides look misaligned.
8. Tell me to open `talks/<short-name>/app/index.html`, and list the keyboard shortcuts.
9. Afterwards, help me when I come back with changes:
   - If I say a word is mispronounced, add a line to `pronunciation.tsv` (written form, spoken form, note), rebuild with `--no-images`, and remind me to reload the page with Ctrl+F5. Try a plain respelling first, and use a phoneme string between slashes only if the respelling still sounds wrong.
   - If I edit the script, rebuild and report the new times.
   - If a slide runs over time, tell me by how many seconds. Suggest cuts only if I ask.

Do not change `build.py` or `app/index.html` unless I ask.

---
