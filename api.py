import db
import time
import datetime
import os
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple admin credentials for login
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")

# Discord OAuth2 credentials and access rules
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://localhost:3000")

GUILD_ID = "1346875447153000529"
ALLOWED_ROLE_IDS = {
    "1347330172067643522",
    "1347330654697689248",
    "1348535790518538250",
    "1347332069348475004",
    "1384521956124262480",
    "1347122745900662835",
    "1347110952260075581",
    "1347122701805948928",
    "1347111842723397673",
    "1347122121469591653",
    "1347122549456240722",
}

db.init_db()


@app.get("/users")
def list_users():
    return db.get_all_users()

@app.get("/users/{user_id}")
def user_detail(user_id: str):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["pointHistory"] = db.get_honey_history(user_id, limit=20)
    user["activityLogs"] = db.get_recent_adventure_logs(user_id, limit=20)
    return user

@app.post("/users/{user_id}/points")
def adjust_points(user_id: str, payload: dict):
    amount = int(payload.get("amount", 0))
    if not amount:
        raise HTTPException(status_code=400, detail="amount required")
    db.add_honey(user_id, amount)
    return {"status": "ok"}


@app.get("/stats/overview")
def stats_overview():
    today = datetime.date.today()
    start_of_day = int(time.mktime(today.timetuple()))
    return {
        "totalUsers": db.get_total_user_count(),
        "registeredUsers": db.get_total_registered_user_count(),
        "totalHoney": db.get_total_honey(),
        "joinedToday": db.get_joined_count_since(start_of_day),
        "registeredToday": db.get_registered_count_since(start_of_day),
        "activeToday": db.get_active_user_count_since(start_of_day),
    }


@app.get("/stats/user-growth")
def user_growth():
    return db.get_user_growth()


@app.get("/logs/bot")
def bot_logs():
    logs = db.get_recent_bot_logs()
    for log in logs:
        log["timestamp"] = datetime.datetime.fromtimestamp(log["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    return logs


@app.get("/logs/admin")
def admin_logs():
    logs = db.get_recent_admin_logs()
    for log in logs:
        log["timestamp"] = datetime.datetime.fromtimestamp(log["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    return logs


@app.post("/login")
def login(payload: dict):
    username = payload.get("username")
    password = payload.get("password")
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"status": "ok"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/discord/login")
def discord_login():
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds.members.read",
    }
    return RedirectResponse(
        "https://discord.com/api/oauth2/authorize?" + urlencode(params)
    )


@app.get("/discord/callback")
async def discord_callback(code: str):
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://discord.com/api/oauth2/token", data=data, headers=headers
        )
        if token_res.status_code != 200:
            return HTMLResponse(
                f"<script>alert('인증 실패');window.location='{WEB_BASE_URL}/login';</script>"
            )
        token = token_res.json()
        access = token.get("access_token")
        headers = {"Authorization": f"Bearer {access}"}
        member_res = await client.get(
            f"https://discord.com/api/users/@me/guilds/{GUILD_ID}/member",
            headers=headers,
        )
        if member_res.status_code != 200:
            return HTMLResponse(
                f"<script>alert('서버에 가입되어 있지 않습니다.');window.location='{WEB_BASE_URL}/login';</script>"
            )
        roles = member_res.json().get("roles", [])
        if not any(role in ALLOWED_ROLE_IDS for role in roles):
            return HTMLResponse(
                f"<script>alert('권한이 없습니다.');window.location='{WEB_BASE_URL}/login';</script>"
            )
    return HTMLResponse(
        f"<script>localStorage.setItem('loggedIn','true');window.location='{WEB_BASE_URL}/'</script>"
    )
