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
