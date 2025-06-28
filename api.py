import db
import time
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()

user_growth_data = [
    {"month": "1월", "joined": 186, "left": 80},
    {"month": "2월", "joined": 305, "left": 200},
    {"month": "3월", "joined": 237, "left": 120},
    {"month": "4월", "joined": 273, "left": 190},
    {"month": "5월", "joined": 209, "left": 130},
    {"month": "6월", "joined": 214, "left": 140},
]

bot_usage_logs = [
    {
        "id": "LOG001",
        "timestamp": "2025-06-29 10:30:15",
        "user": {"name": "모험적인유저", "avatar": "/placeholder.svg?height=32&width=32"},
        "command": "/모험",
        "details": "성공 - 50 꿀 획득",
    },
    {
        "id": "LOG002",
        "timestamp": "2025-06-29 10:28:45",
        "user": {"name": "관대한기부자", "avatar": "/placeholder.svg?height=32&width=32"},
        "command": "/허니선물",
        "details": "모험적인유저에게 100 꿀 선물",
    },
    {
        "id": "LOG003",
        "timestamp": "2025-06-28 10:25:02",
        "user": {"name": "새로운참가자", "avatar": "/placeholder.svg?height=32&width=32"},
        "command": "/가입",
        "details": "신규 가입 완료",
    },
    {
        "id": "LOG004",
        "timestamp": "2025-06-28 10:20:11",
        "user": {"name": "모험적인유저", "avatar": "/placeholder.svg?height=32&width=32"},
        "command": "/모험",
        "details": "실패 - 20 꿀 잃음",
    },
    {
        "id": "LOG005",
        "timestamp": "2025-06-27 10:15:55",
        "user": {"name": "관리자마스터", "avatar": "/placeholder.svg?height=32&width=32"},
        "command": "/지급",
        "details": "관대한기부자에게 1000 꿀 지급",
    },
]

admin_logs_data = [
    {
        "id": "ALOG001",
        "timestamp": "2025-06-29 14:10:25",
        "admin": {"name": "관리자마스터", "avatar": "/placeholder.svg?height=32&width=32"},
        "targetUser": {"name": "모험적인유저"},
        "action": "포인트 지급",
        "details": "1,000 꿀 (사유: 주간 이벤트 우승 보상)",
    },
    {
        "id": "ALOG002",
        "timestamp": "2025-06-29 11:05:11",
        "admin": {"name": "부관리자", "avatar": "/placeholder.svg?height=32&width=32"},
        "targetUser": {"name": "관대한기부자"},
        "action": "포인트 차감",
        "details": "500 꿀 (사유: 시스템 오류로 인한 과지급 회수)",
    },
    {
        "id": "ALOG003",
        "timestamp": "2025-06-28 18:30:00",
        "admin": {"name": "관리자마스터", "avatar": "/placeholder.svg?height=32&width=32"},
        "targetUser": {"name": "새로운참가자"},
        "action": "포인트 지급",
        "details": "200 꿀 (사유: 버그 제보 보상)",
    },
]

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
    return user_growth_data


@app.get("/logs/bot")
def bot_logs():
    return bot_usage_logs


@app.get("/logs/admin")
def admin_logs():
    return admin_logs_data
