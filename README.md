# flang-bot

이 저장소는 간단한 디스코드 봇 예제입니다. 봇은 `/커맨드` 슬래시 커맨드를 사용하여 인사를 반환합니다.

## 사용 방법

1. 필요한 라이브러리를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

2. 루트 디렉터리에 `.env` 파일을 만들고 다음과 같이 봇 토큰을 설정합니다:
   ```env
   DISCORD_TOKEN=여러분의봇토큰
   ```
   혹은 `DISCORD_TOKEN` 환경 변수를 직접 설정해도 됩니다.

3. `bot.py`를 실행하여 봇을 시작합니다:
   ```bash
   python bot.py
   ```

봇이 온라인 상태가 되면 Discord 서버에서 `/커맨드`를 실행하여 동작을 확인할 수 있습니다.
