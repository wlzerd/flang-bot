# flang-bot

이 저장소는 간단한 디스코드 봇 예제입니다. 봇은 `/인사`, `/가입`, `/꿀단지`, `/허니 선물`, `/지급`, `/모험`, `/모험기록`, `/채널` 여덟 가지 명령을 제공합니다.
`/인사`는 인사 메시지를 반환하고, `/가입`은 명령을 실행한 사용자의 정보를 SQLite 데이터베이스에 저장합니다. 저장되는 정보에는 아이디와 사용자 이름은 물론 프로필 이미지 URL과 명령을 실행한 서버에서의 닉네임도 포함됩니다. `/꿀단지` 명령을 사용하면 저장된 자신의 이름과 포인트인 **허니**를 확인하고 프로필 이미지를 임베드의 왼쪽에 표시합니다. `/허니 선물` 명령을 사용하면 다른 사용자에게 보유한 허니를 선물할 수 있습니다. `/지급` 명령으로 관리자가 사유와 함께 허니를 지급할 수도 있습니다. 이 명령은 Discord에서 **관리자 권한**을 가진 사용자만 사용할 수 있습니다. 또한 `/모험` 명령으로 원하는 레벨을 선택해 모험을 시도할 수 있습니다.
`/모험기록` 명령으로 최근 모험 결과 5개를 임베드로 확인할 수 있습니다.
허니를 받은 사용자는 DM으로 "선물이 도착했어요!" 임베드를 받아 누가 얼마만큼 보냈는지 확인할 수 있습니다.
`/채널` 명령을 사용하면 관리자가 봇 명령을 허용할 텍스트 채널을 지정할 수 있습니다.
이 명령을 여러 번 호출하면 여러 채널을 허용 목록에 추가할 수 있습니다.

## 사용 방법

1. 필요한 라이브러리를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

2. 루트 디렉터리에 `.env` 파일을 만들고 다음과 같이 설정합니다:
   ```env
   DISCORD_TOKEN=여러분의봇토큰
   DISCORD_CLIENT_ID=애플리케이션의클라이언트ID
   DISCORD_CLIENT_SECRET=애플리케이션의클라이언트시크릿
   DISCORD_REDIRECT_URI=http://localhost:8000/discord/callback
   WEB_BASE_URL=http://localhost:3000
   ```
   `DISCORD_CLIENT_ID`와 `DISCORD_CLIENT_SECRET`은 Discord 개발자 포털에서 확인할 수 있으며,
   `DISCORD_REDIRECT_URI` 값도 같은 포털의 OAuth2 설정에서 허용된 Redirect URI로 등록해야 합니다.
   `WEB_BASE_URL`은 로그인 후 이동할 웹 대시보드의 주소를 의미합니다.
   혹은 `DISCORD_TOKEN` 환경 변수를 직접 설정해도 됩니다.

3. `bot.py`를 실행하여 봇을 시작합니다:
   ```bash
   python bot.py
   ```

사용자 정보는 같은 디렉터리에 생성되는 `users.db` SQLite 파일에 저장됩니다.

봇이 온라인 상태가 되면 Discord 서버에서 `/인사` 혹은 `/가입`을 실행하여 동작을 확인할 수 있습니다.

텍스트 채팅을 작성하면 1 허니가 적립되고, 음성 채널에 접속해 있는 사용자는 60초에 한 번씩 0.5 허니가 자동으로 추가됩니다.

## 예제: 허니 적립

`honey_counter.py` 파일에는 텍스트 채팅 시 1 허니, 음성 채팅 시 0.5 허니를 적립하고 소수점 첫째 자리까지만 표시하는 간단한 예제가 담겨 있습니다.

```python
from honey_counter import User

user = User()
user.add_text_chat()
user.add_voice_chat()
print(user.get_honey_str())  # '1.5'
```

## Docker로 실행하기

docker compose를 사용하면 로컬에 파이썬을 설치하지 않고도 봇을 실행할 수 있습니다. 먼저 `.env` 파일을 만들어 다음과 같이 환경 변수를 설정합니다.

```env
DISCORD_TOKEN=여러분의봇토큰
DISCORD_CLIENT_ID=애플리케이션의클라이언트ID
DISCORD_CLIENT_SECRET=애플리케이션의클라이언트시크릿
DISCORD_REDIRECT_URI=http://localhost:8000/discord/callback
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
WEB_BASE_URL=http://localhost:3000
```

이 값들은 빌드 단계에서도 자동으로 주입되므로, 변경 후에는 다시 이미지를 빌드해야 합니다.

```bash
docker compose build
docker compose up
```

`api` 서비스가 함께 실행되어 웹 대시보드에서 데이터를 조회할 수 있습니다. 기본적으로
`http://localhost:8000` 에서 API가 동작하므로 위 `.env` 파일의
`NEXT_PUBLIC_API_BASE_URL` 값도 동일하게 유지해야 합니다.

컨테이너는 `users.db` 파일을 호스트와 공유하므로 데이터를 유지한 채 재시작할 수 있습니다.

## 데이터베이스 마이그레이션

업데이트로 `member_events` 테이블이 추가되었습니다. 기존 배포에서 테이블을 생성하려면 다음 명령을 실행합니다.

```bash
sqlite3 users.db < migrations/001_create_member_events.sql
```

봇이나 API를 재시작하면 새 테이블이 자동으로 사용됩니다.
