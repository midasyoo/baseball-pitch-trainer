# 1분 홍보 영상 만들기

`baseball-pitch-trainer-1min.mp4` (1920×1080 · 24fps · 60.00s) 를 다시 만드는 도구.

## 원리

앱 화면을 실시간으로 녹화하지 않는다. 캡처는 초당 1~2장밖에 안 나오므로 녹화하면
영상이 끊긴다. 대신 `index.html` 의 `#cap=1` 훅(`window.__CAP`)으로 **프레임마다
애니메이션 시점 `t` 와 카메라 각도를 직접 지정해 한 장씩 렌더**한다. 캡처가 얼마나
느리든 결과는 항상 같다.

## 구성

| 파일 | 역할 |
|---|---|
| `bp_story.py` | 스토리보드 — 샷 순서·길이·자막. **내용을 바꾸려면 여기만 고친다** |
| `bpshot.py` | 헤드리스 Chrome 을 CDP 로 붙잡는 얇은 래퍼 |
| `bp_capture.py` | 스토리보드대로 원본 프레임 캡처 (중단 후 재개 가능) |
| `bp_compose.py` | 원본 위에 한글 자막·챕터 카드 합성 |

## 실행

```bash
pip install websocket-client pillow imageio-ffmpeg

python tools/promo/bp_story.py                    # 구성 확인 (샷 목록·길이)
python tools/promo/bp_capture.py                  # 프레임 캡처 (약 20분)
python tools/promo/bp_compose.py                  # 자막 합성

python -c "import imageio_ffmpeg as f;print(f.get_ffmpeg_exe())"   # ffmpeg 경로
<ffmpeg> -y -framerate 24 -i tools/promo/_work/bp_out/f%05d.png \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -movflags +faststart \
  baseball-pitch-trainer-1min.mp4
```

작업 파일은 `tools/promo/_work/` 에 쌓인다 (`PROMO_WORK` 로 바꿀 수 있다).
이미 있는 프레임은 건너뛰므로 중간에 끊겨도 다시 실행하면 이어서 한다.

## 구성안 (60초)

| 시각 | 구간 | 내용 |
|---|---|---|
| 0:00 | 타이틀 | 4초 |
| 0:04 | **① 원리 이해** | 챕터 카드 3초 |
| 0:07 | · ① 그립 → ⑤ 궤적 | 각 4~5초, 슬라이더 기준 |
| 0:28 | · 타자의 시점 | 4초 |
| 0:32 | · 6구종 | 투심·싱커·슬라이더·커브·포크·너클 — 그립 1초 + 타자 시점 궤적 1초 |
| 0:44 | **② 실제 연습** | 챕터 카드 2초 |
| 0:46 | · 그립 따라 하기 · 카메라 그립 체크 · 자가진단 | 각 3.7초 |
| 0:57 | 클로징 | 3초 |
