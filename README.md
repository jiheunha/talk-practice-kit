# talk-practice-kit

Practice an English talk on your own computer. You give the kit your script and your slide deck as a PDF, and it builds a web page with the slide on the left and the script on the right. A local text-to-speech model (Kokoro-82M) reads the script aloud, and the page highlights the sentence being read. Nothing is sent online: the script and the deck stay on your computer. The rest of this README is in Korean.

![Example app](docs/screenshot.png)

## 무엇을 하나요

영어 발표 스크립트(`script.md`)와 슬라이드 PDF를 넣으면 연습용 웹 페이지를 만들어 줍니다.

- 왼쪽에 슬라이드, 오른쪽에 스크립트가 보입니다.
- 로컬 TTS(Kokoro-82M, CPU)가 스크립트를 읽어 주고, 읽고 있는 문장이 강조됩니다.
- 슬라이드별 음성 길이와 목표 시간을 비교해서 시간이 넘으면 표시합니다.
- 서버 없이 `index.html`을 더블클릭하면 열립니다.

## 설치

Python 3.12 또는 3.13이 필요합니다 (3.14는 아직 지원하지 않습니다). 디스크 여유 공간은 약 1.5 GB가 필요하고, 그중 모델 파일이 약 350 MB입니다.

```
git clone <이 저장소 주소>
cd talk-practice-kit
```

Windows:

```
py -3.13 setup_kit.py
```

macOS:

```
python3.13 setup_kit.py
```

`setup_kit.py`는 `.venv`를 만들고, `requirements.txt`의 패키지를 설치하고, `get_models.py`로 모델 파일 두 개를 `models/`에 내려받아 sha256을 확인합니다. 다시 실행해도 끝난 단계는 건너뜁니다.

설치가 끝나면 예제 발표로 확인해 보세요 (1분 정도 걸립니다).

Windows:

```
.venv\Scripts\python build.py --script example/script.md --deck example/deck.pdf --out example/app
```

macOS:

```
.venv/bin/python build.py --script example/script.md --deck example/deck.pdf --out example/app
```

그다음 `example/app/index.html`을 Chrome에서 엽니다.

Claude Code를 쓴다면 [PROMPT_for_lab.md](PROMPT_for_lab.md)의 프롬프트를 붙여 넣으면 설치부터 빌드까지 도와줍니다.

## 내 발표 만들기

1. `talks/<이름>/` 폴더를 만들고 `script.md`와 `deck.pdf`를 넣습니다.
2. 빌드합니다 (macOS에서는 `.venv/bin/python`).

```
.venv\Scripts\python build.py --script talks/<이름>/script.md --deck talks/<이름>/deck.pdf --out talks/<이름>/app
```

3. `talks/<이름>/app/index.html`을 엽니다.

발표마다 `app/` 폴더가 따로 생기므로 여러 발표를 나란히 둘 수 있습니다.

옵션:

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| `--voice` | `af_heart` | Kokoro 음성 이름 (예: `af_bella`, `am_michael`) |
| `--speed` | `0.85` | 합성 속도. 1.0이 모델의 기본 속도입니다 |
| `--no-images` | | 슬라이드 이미지를 다시 만들지 않습니다 (`--deck` 생략 가능) |

문장 사이에는 0.4초, 문단 사이에는 0.7초 쉽니다.

### 스크립트를 고친 뒤

같은 빌드 명령을 다시 실행하고, 브라우저에서 Ctrl+F5(macOS는 Cmd+Shift+R)로 새로고침합니다. 문장별 음성은 텍스트, 음성, 속도를 기준으로 `cache/`에 저장되므로 바뀐 문장만 다시 합성합니다. 슬라이드가 그대로라면 `--no-images`를 붙이면 더 빠릅니다.

## 스크립트 형식

```markdown
## Slide 1. A weather station on the roof (0:20)

*Smile and wait for the room to settle.*

Good afternoon, everyone. Last spring our lab put a small weather station on the roof.

Today I will show you what we measured.

## Slide 2. What we measured (0:30)

The station records temperature every ten minutes.
```

- 슬라이드는 `## Slide N. 제목 (m:ss)`로 시작합니다. `(m:ss)`는 그 슬라이드의 목표 시간이고, 음성이 이보다 길면 앱에 주황색으로 표시됩니다.
- 목표 시간은 생략할 수 있습니다. 시간이 없는 슬라이드는 앱에서 appendix로 취급합니다. 전체 시간 합계에서 빠지고, 자동으로 다음 슬라이드로 넘어갈 때 그 앞에서 멈춥니다. 본 발표 슬라이드에는 시간을 적어 주세요.
- 문단 사이에는 빈 줄을 둡니다. 한 문단은 한 줄로 씁니다.
- `*...*`로 감싼 줄은 메모입니다. 앱에는 보이지만 읽지 않습니다. 슬라이드당 하나만 표시됩니다.
- 숫자와 약어는 말하는 대로 적습니다. 예: `2030` 대신 `twenty thirty`, `KAIST`를 한 글자씩 읽으려면 `K-A-I-S-T`. 스크립트를 그대로 두고 싶으면 `pronunciation.tsv`에 한 줄 추가합니다.
- 슬라이드 PDF는 슬라이드당 한 페이지, 스크립트와 같은 순서여야 합니다. PowerPoint의 "PDF로 저장"이면 됩니다. 애니메이션이 있는 슬라이드는 마지막 상태가 보입니다.

### 발음 고치기 (`pronunciation.tsv`)

탭으로 구분한 세 칸입니다: 쓴 형태, 읽는 형태, 메모.

```
QR	Q-R
CO2	carbon dioxide
Daejeon	/dˈɛʤʌn/	DEH-jun
```

읽는 형태는 그냥 영어로 적거나, 슬래시 사이에 misaki 음소를 적습니다. 대소문자를 구분하고 단어 전체가 일치할 때만 적용됩니다. 고친 뒤에는 다시 빌드합니다.

## 키보드 단축키

| 키 | 동작 |
| --- | --- |
| Space | 재생 / 일시정지 |
| ← / → | 이전 / 다음 문장 |
| PageUp / PageDown | 이전 / 다음 슬라이드 |
| 문장 클릭 | 그 문장부터 재생 |

화면 아래에서 재생 속도, 글자 크기, 다음 슬라이드로 자동 진행 여부를 바꿀 수 있습니다. 다크 모드는 시스템 설정을 따릅니다.

## 개인정보

모든 과정이 내 컴퓨터에서 실행됩니다. 스크립트와 슬라이드는 온라인으로 전송되지 않습니다. 인터넷은 설치할 때 패키지와 모델 파일을 내려받는 데만 씁니다.

`talks/` 안의 파일은 `.gitignore`에 들어 있어서 실수로 commit되지 않습니다. 스크립트와 발표 자료는 `talks/` 안에 두세요.

## 라이선스

이 kit의 코드는 MIT 라이선스입니다 ([LICENSE](LICENSE)). 아래 구성 요소는 설치할 때 내려받으며 이 저장소에는 들어 있지 않습니다.

- Kokoro-82M (모델): Apache-2.0
- kokoro-onnx: MIT
- misaki: Apache-2.0
- 그 밖에 PyMuPDF(AGPL-3.0), espeak-ng(GPL-3.0), LAME(LGPL) 등은 각자의 라이선스를 따릅니다.
