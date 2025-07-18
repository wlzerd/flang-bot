import os
import time
import uuid
from dataclasses import dataclass
import random
import datetime
import asyncio

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

import db

load_dotenv()
# Set timezone to Korea Standard Time
os.environ["TZ"] = "Asia/Seoul"
try:
    time.tzset()
except AttributeError:
    pass
TOKEN = os.getenv('DISCORD_TOKEN')

description = "간단한 디스코드 봇"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 허니 모임 위한 그룹
honey_group = app_commands.Group(name="허니", description="허니 관련 명령")
# 랭킹 명령 그룹
ranking_group = app_commands.Group(name="랭킹", description="랭킹 관련 명령")


def log_command(interaction: discord.Interaction, command: str, details: str = ""):
    try:
        db.add_bot_log(str(interaction.user.id), command, details)
    except Exception as e:
        print(f"Failed to log command: {e}")

# Adventure level settings
ADVENTURE_LEVELS = [
    {
        "name": "새싹들판",
        "success": 90,
        "reward": 50,
        "banner": "banner/Lv1.gif",
        "success_desc": "> 플로비가 부드러운 바람을 따라 들판을 누비다가 . . .",
        "fail_desc": "> 플로비가 나비를 따라가다 길을 잃어버리면서 . . .",
    },
    {
        "name": "튤립정원",
        "success": 75,
        "reward": 150,
        "banner": "banner/Lv2.gif",
        "success_desc": "> 플로비가 알록달록한 튤립 사이를 누비다가 . . .",
        "fail_desc": "> 플로비가 튤립 속에 숨은 벌레를 보고 깜짝 놀라 . . .",
    },
    {
        "name": "라벤더숲",
        "success": 60,
        "reward": 300,
        "banner": "banner/Lv3.gif",
        "success_desc": "> 플로비가 보라빛 향기에 이끌려 숲을 탐험하다가 . . .",
        "fail_desc": "> 플로비가 숲속 깊이 들어갔다가 길을 잃고 . . .",
    },
    {
        "name": "가시덤불",
        "success": 35,
        "reward": 500,
        "banner": "banner/Lv4.gif",
        "success_desc": "> 플로비가 가시 사이를 날아다니며 꿀을 찾고 . . .",
        "fail_desc": "> 플로비가 가시에 찔릴 뻔해서 황급히 도망치다가 . . .",
    },
    {
        "name": "여왕벌궁",
        "success": 25,
        "reward": 1000,
        "banner": "banner/Lv5.gif",
        "success_desc": "> 플로비가 여왕벌의 눈을 피해 궁을 탐험하다 . . .",
        "fail_desc": "> 플로비가 경비벌 에게 들켜 도망치다 . . .",
    },
]

# Flower gacha items
FLOWER_ITEMS = [
    {
        "name": "데이지",
        "rarity": "커먼",
        "weight": 60,
        "effect": "honey_plus",
        "value": 10,
        "description": "허니 10 획득",
    },
    {
        "name": "민들레",
        "rarity": "커먼",
        "weight": 60,
        "effect": "adventure_success_bonus",
        "value": 5,
        "description": "다음 모험 성공 확률 5% 증가",
    },
    {
        "name": "코스모스",
        "rarity": "커먼",
        "weight": 60,
        "effect": "chat_double",
        "description": "채팅 허니 두 배",
    },
    {
        "name": "튤립",
        "rarity": "에픽",
        "weight": 25,
        "effect": "voice_double",
        "description": "음성 채팅 허니 두 배",
    },
    {
        "name": "장미",
        "rarity": "에픽",
        "weight": 25,
        "effect": "gift_bonus",
        "description": "선물 시 10% 추가 지급",
    },
    {
        "name": "해바라기",
        "rarity": "에픽",
        "weight": 25,
        "effect": "cooldown_half",
        "description": "모험 대기 시간 절반",
    },
    {
        "name": "라벤더",
        "rarity": "레어",
        "weight": 10,
        "effect": "adventure_reward_bonus",
        "value": 0.5,
        "description": "모험 보상 50% 증가",
    },
    {
        "name": "수국",
        "rarity": "레어",
        "weight": 10,
        "effect": "free_adventure",
        "description": "다음 모험 쿨타임 제거",
    },
    {
        "name": "동백꽃",
        "rarity": "레어",
        "weight": 10,
        "effect": "gift_cashback",
        "description": "선물한 허니 캐시백",
    },
    {
        "name": "벚꽃",
        "rarity": "전설",
        "weight": 5,
        "effect": "all_honey_double",
        "description": "모든 허니 획득량 두 배",
    },
    {
        "name": "달맞이꽃",
        "rarity": "전설",
        "weight": 5,
        "effect": "adventure_auto_success",
        "description": "최고 레벨 모험 즉시 성공",
    },
    {
        "name": "별꽃",
        "rarity": "전설",
        "weight": 5,
        "effect": "honey_plus",
        "value": 500,
        "description": "허니 500 획득",
    },
]


@bot.tree.interaction_check
async def check_allowed_channel(interaction: discord.Interaction) -> bool:
    """Restrict command usage to the configured channel for the guild."""
    if interaction.guild is None:
        return True
    if interaction.command and interaction.command.name == "채널":
        return True
    allowed = db.get_allowed_channels(str(interaction.guild.id))
    if allowed and str(interaction.channel_id) not in allowed:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "이 채널에서는 명령을 사용할 수 없습니다.", ephemeral=True
            )
        return False
    return True


@dataclass
class VoiceSession:
    session_id: str
    user_id: str
    last_award: float


voice_sessions: dict[int, VoiceSession] = {}


def get_effect_map(user_id: str) -> dict[str, dict]:
    effects = db.get_active_effects(user_id)
    return {e["effect"]: e for e in effects}


def apply_flower_effect(user_id: str, item: dict) -> str:
    effect = item.get("effect")
    effects = get_effect_map(user_id)
    if effect != "honey_plus" and effect in effects:
        return f"{item['name']} 효과가 이미 적용 중입니다!"

    if effect == "honey_plus":
        db.add_honey(user_id, item.get("value", 0))
        return f"{item['name']}을(를) 얻어 {item.get('value', 0)} 허니를 획득했습니다!"
    if effect == "adventure_auto_success":
        level = ADVENTURE_LEVELS[-1]
        db.add_honey(user_id, level["reward"])
        db.add_adventure_log(user_id, "성공", level["reward"], level["reward"])
        return f"{item['name']}의 힘으로 {level['name']} 모험을 성공해 {level['reward']} 허니를 얻었습니다!"

    data = {"value": item.get("value"), "item_name": item.get("name")}
    db.add_effect(user_id, effect, 0, data)
    detail = f"({item.get('description')})" if item.get("description") else ""
    return f"{item['name']} 효과{detail}가 영구적으로 적용됩니다!"


async def run_adventure(interaction: discord.Interaction, level: dict):
    """Handle adventure logic for a given level."""
    user_id = str(interaction.user.id)
    if not db.get_user(user_id):
        await interaction.response.send_message("먼저 /가입을 해주세요.", ephemeral=True)
        return
    effects = get_effect_map(user_id)
    cooldown_until = db.get_adventure_cooldown(user_id)
    now = int(time.time())
    if "free_adventure" in effects:
        db.remove_effect(user_id, "free_adventure")
        cooldown_until = now
    if cooldown_until > now:
        remaining = cooldown_until - now
        minutes, seconds = divmod(remaining, 60)
        cooldown_str = f"{minutes}분 {seconds}초"
        embed = discord.Embed(
            description=f"{cooldown_str} 뒤에 사용할 수 있어요",
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    start_embed = discord.Embed(
        description=f"## <a:emoji_146:1372097429834432532> {level['name']} 모험 준비중 ⸝⸝ \n> 플로비가 모험을 준비 중입니다 . . .",
        color=discord.Color.gold(),
    )
    file_name = os.path.basename(level["banner"])
    file = discord.File(level["banner"], filename=file_name)
    start_embed.set_image(url=f"attachment://{file_name}")
    await interaction.response.send_message(embed=start_embed, file=file)

    await asyncio.sleep(10)
    bonus = effects.get("adventure_success_bonus", {}).get("data", {}).get("value", 0)
    success = random.random() * 100 < (level["success"] + bonus)
    if "adventure_success_bonus" in effects:
        db.remove_effect(user_id, "adventure_success_bonus")
    desc = level.get("success_desc" if success else "fail_desc", "")

    desc_embed = discord.Embed(
        description=f"## <a:emoji_146:1372097429834432532> {level['name']} 모험 결과 ⸝⸝ \n{desc}",
        color=discord.Color.gold(),
    )
    desc_file = discord.File(level["banner"], filename=file_name)
    desc_embed.set_image(url=f"attachment://{file_name}")
    await interaction.edit_original_response(embed=desc_embed, attachments=[desc_file])

    await asyncio.sleep(10)
    reward = level["reward"]
    reward_bonus = effects.get("adventure_reward_bonus", {}).get("data", {}).get("value", 0)
    if reward_bonus:
        reward = int(reward * (1 + reward_bonus))
    if success:
        db.add_honey(user_id, reward)
        db.add_adventure_log(user_id, "성공", reward, reward)
        result_text = f"## <a:emoji_85:1363445329483006132>**모험성공**! \n> {reward} 허니를 얻었어요"
    else:
        db.add_adventure_log(user_id, "실패", level["reward"], 0)
        result_text = "**모험실패**!"

    result_embed = discord.Embed(
        description=f"## <a:emoji_146:1372097429834432532> {level['name']} 모험 결과 ⸝⸝ \n{desc} \n{result_text}",
        color=discord.Color.gold(),
    )
    result_file = discord.File(level["banner"], filename=file_name)
    result_embed.set_image(url=f"attachment://{file_name}")
    await interaction.edit_original_response(embed=result_embed, attachments=[result_file])
    cooldown_seconds = 180 if success else 1800
    if "cooldown_half" in effects:
        cooldown_seconds = cooldown_seconds // 2
    db.set_adventure_cooldown(user_id, int(time.time()) + cooldown_seconds)
    result = "성공" if success else "실패"
    log_command(interaction, "/모험", f"{level['name']} {result} {reward if success else 0}허니")


async def ensure_user_record(user: discord.abc.User, guild: discord.Guild | None = None):
    existing = db.get_user(str(user.id))
    if existing:
        return
    avatar_url = None
    try:
        avatar_url = user.display_avatar.url
    except Exception:
        pass
    nick = None
    if guild:
        member = guild.get_member(user.id)
        if member:
            nick = member.nick
    if nick is None:
        nick = getattr(user, "nick", None)
    discriminator = user.discriminator or ""
    db.add_or_update_user(
        str(user.id),
        user.name,
        discriminator,
        avatar_url,
        nick,
        0,
        False,
    )


@tasks.loop(seconds=60)
async def tick_voice_sessions():
    """Award honey to users connected to voice channels."""
    now = time.time()
    for session in list(voice_sessions.values()):
        effects = get_effect_map(session.user_id)
        mult = 1
        if "voice_double" in effects:
            mult *= 2
        if "all_honey_double" in effects:
            mult *= 2
        db.add_honey(session.user_id, 0.5 * mult)
        session.last_award = now


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    info = db.get_user(str(message.author.id))
    if info:
        effects = get_effect_map(str(message.author.id))
        mult = 1
        if "chat_double" in effects:
            mult *= 2
        if "all_honey_double" in effects:
            mult *= 2
        db.add_honey(str(message.author.id), mult)
    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel is None and after.channel is not None:
        if db.get_user(str(member.id)):
            voice_sessions[member.id] = VoiceSession(
                session_id=str(uuid.uuid4()),
                user_id=str(member.id),
                last_award=time.time(),
            )
    elif before.channel is not None and after.channel is None:
        voice_sessions.pop(member.id, None)


@bot.event
async def on_member_join(member: discord.Member):
    await ensure_user_record(member, member.guild)
    joined_ts = int(member.joined_at.timestamp()) if member.joined_at else int(time.time())
    db.update_joined_at(str(member.id), joined_ts)
    db.set_member_status(str(member.id), True)
    db.add_member_event(str(member.id), "joined")


@bot.event
async def on_member_remove(member: discord.Member):
    db.set_member_status(str(member.id), False)
    db.add_member_event(str(member.id), "left")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        GUILD_ID = 850766852148822026
        print(f"Synced {len(synced)} commands")
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    await bot.change_presence(
        activity=discord.Game(name="🍯 허니 수확")  # 또는 "플로비와 대화 중" 등
    )
    if not tick_voice_sessions.is_running():
        tick_voice_sessions.start()

    # ensure the database reflects current guild membership
    for guild in bot.guilds:
        member_ids = set()
        async for m in guild.fetch_members(limit=None):
            member_ids.add(str(m.id))
            await ensure_user_record(m, guild)
            joined_ts = int(m.joined_at.timestamp()) if m.joined_at else int(time.time())
            db.update_joined_at(str(m.id), joined_ts)
            db.set_member_status(str(m.id), True)

        existing_ids = {u["user_id"] for u in db.get_all_users()}
        for uid in existing_ids - member_ids:
            db.set_member_status(uid, False)


@app_commands.command(name="인사", description="인사 메시지")
async def greet_command(interaction: discord.Interaction):
    await interaction.response.send_message("안녕하세요!", ephemeral=True)
    log_command(interaction, "/인사")


@app_commands.command(name="가입", description="봇 서비스를 위한 가입")
async def join_command(interaction: discord.Interaction):
    user = interaction.user
    avatar_url = None
    try:
        avatar_url = user.display_avatar.url
    except Exception:
        pass
    nick = None
    if interaction.guild:
        member = interaction.guild.get_member(user.id)
        if member:
            nick = member.nick
    if nick is None:
        nick = getattr(user, "nick", None)
    existing = db.get_user(str(user.id))
    honey = existing.get("honey", 0) if existing else 0
    discriminator = user.discriminator or ""
    db.add_or_update_user(
        str(user.id),
        user.name,
        discriminator,
        avatar_url,
        nick,
        honey,
        True,
    )
    await interaction.response.send_message(
        f"{user.name}님의 정보가 저장되었습니다.", ephemeral=True
    )
    log_command(interaction, "/가입")


@app_commands.command(name="꿀단지", description="저장된 유저 정보 보기")
async def honey_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    info = db.get_user(user_id)
    if not info:
        await interaction.response.send_message(
            "저장된 정보가 없습니다. /가입 명령으로 등록해주세요.",
            ephemeral=True,
        )
        return

    avatar_url = info.get("avatar_url")
    if not avatar_url:
        try:
            avatar_url = interaction.user.display_avatar.url
        except Exception:
            avatar_url = None

    embed = discord.Embed(color=discord.Color.gold())
    display_name = info.get("nick") or info.get("name") or "알수없음"
    discriminator = info.get("discriminator")
    author_name = display_name if not discriminator else f"{display_name}"
    embed.set_author(
        name=author_name,
        icon_url=avatar_url,
    )
    embed.add_field(
        name="Ny허니",
        value=f"[{str(info.get('honey', 0))}] 허니를 보유하고 있습니다!",
        inline=False,
    )

    effects = db.get_active_effects(user_id)
    if effects:
        effect_lines = []
        for eff in effects:
            data = eff.get("data") or {}
            raw_item_name = data.get("item_name", eff.get("effect"))

            item = next(
                (it for it in FLOWER_ITEMS if it["name"] == raw_item_name or it["effect"] == raw_item_name),
                None
            )

            item_name = item.get("name", raw_item_name) if item else raw_item_name
            rarity = item.get("rarity", "?") if item else "?"
            description = (
                item.get("description")
                if item and item.get("description")
                else data.get("description") or eff.get("effect")
            )

            effect_lines.append(f"**{item_name} ({rarity})**: {description}")

        # 하나의 필드로 통합해서 여백 줄이기
        embed.add_field(
            name="보유 중인 효과",
            value="\n".join(effect_lines),
            inline=False,
        )

    await interaction.response.send_message(embed=embed, ephemeral=False)
    log_command(interaction, "/꿀단지")


@honey_group.command(name="선물", description="다른 사용자에게 허니를 선물합니다")
@app_commands.describe(user="허니를 받을 사용자", amount="선물할 허니 양")
async def gift_honey(
    interaction: discord.Interaction,
    user: discord.Member,
    amount: app_commands.Range[int, 1],
):
    sender_id = str(interaction.user.id)
    receiver_id = str(user.id)
    if not db.get_user(sender_id):
        await interaction.response.send_message(
            "먼저 /가입을 해주세요.", ephemeral=True
        )
        return
    if not db.get_user(receiver_id):
        await interaction.response.send_message(
            "받는 사용자가 아직 가입하지 않았습니다.", ephemeral=True
        )
        return

    if sender_id == receiver_id:
        await interaction.response.send_message(
            "자신에게는 허니를 선물할 수 없습니다.", ephemeral=True
        )
        return

    success = db.transfer_honey(sender_id, receiver_id, amount)
    if not success:
        await interaction.response.send_message(
            "허니가 부족합니다.", ephemeral=True
        )
        return

    sender_effects = get_effect_map(sender_id)
    if "gift_bonus" in sender_effects:
        bonus = int(amount * 0.1)
        db.add_honey(receiver_id, bonus)
    if "gift_cashback" in sender_effects:
        db.add_honey(sender_id, amount)

    await interaction.response.send_message(
        f"{user.mention}에게 {amount} 허니를 선물했습니다!",
        ephemeral=True,
    )
    log_command(interaction, "/허니선물", f"{user.display_name}에게 {amount} 선물")

    # Notify the receiver via DM with an embed
    sender_display = getattr(interaction.user, "display_name", interaction.user.name)
    embed = discord.Embed(
        title="선물이 도착했어요!", color=discord.Color.gold()
    )
    embed.add_field(
        name="​",
        value=f"{sender_display}님이 {amount}허니를 보냈어요!",
        inline=False,
    )
    try:
        await user.send(embed=embed)
    except Exception:
        pass





@app_commands.command(name="모험", description="레벨을 선택해 모험을 진행합니다")
@app_commands.describe(level="도전할 모험 레벨")
@app_commands.choices(
    level=[
        app_commands.Choice(name=lv["name"], value=i)
        for i, lv in enumerate(ADVENTURE_LEVELS)
    ]
)
async def adventure(
    interaction: discord.Interaction, level: app_commands.Choice[int]
):
    await run_adventure(interaction, ADVENTURE_LEVELS[level.value])




@app_commands.command(name="모험기록", description="최근 모험 기록을 확인합니다")
async def adventure_logs_command(interaction: discord.Interaction):
    if not db.get_user(str(interaction.user.id)):
        await interaction.response.send_message(
            "먼저 /가입을 해주세요.", ephemeral=True
        )
        return
    logs = db.get_recent_adventure_logs(str(interaction.user.id), 5)
    if not logs:
        await interaction.response.send_message("모험 기록이 없습니다.", ephemeral=True)
        return

    embed = discord.Embed(title="최근 모험 기록", color=discord.Color.gold())
    for log in logs:
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(log["timestamp"])))
        change = f"{log['change']:+d}"
        embed.add_field(
            name=ts,
            value=f"{log['result']} (변동 {change} 허니)",
            inline=False,
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    log_command(interaction, "/모험기록")


@ranking_group.command(name="주간", description="일주일 동안 획득한 허니 랭킹")
async def weekly_ranking(interaction: discord.Interaction):
    if not db.get_user(str(interaction.user.id)):
        await interaction.response.send_message(
            "먼저 /가입을 해주세요.", ephemeral=True
        )
        return
    today = datetime.datetime.now()
    start = today - datetime.timedelta(days=today.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(days=7)
    ranking = db.get_earned_ranking(int(start.timestamp()), int(end.timestamp()))

    embed = discord.Embed(title="주간 허니 랭킹", color=discord.Color.gold())
    if not ranking:
        embed.add_field(name="​", value="데이터가 없습니다.", inline=False)
    for idx, row in enumerate(ranking, start=1):
        name = row["nick"] or row["name"]
        embed.add_field(name=f"{idx}위 - {name}", value=f"+{row['earned']}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=False)
    log_command(interaction, "/랭킹 주간")


@ranking_group.command(name="월간", description="한 달 동안 획득한 허니 랭킹")
async def monthly_ranking(interaction: discord.Interaction):
    if not db.get_user(str(interaction.user.id)):
        await interaction.response.send_message(
            "먼저 /가입을 해주세요.", ephemeral=True
        )
        return
    now = datetime.datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1)
    else:
        next_month = start.replace(month=start.month + 1)
    ranking = db.get_earned_ranking(int(start.timestamp()), int(next_month.timestamp()))

    embed = discord.Embed(title="월간 허니 랭킹", color=discord.Color.gold())
    if not ranking:
        embed.add_field(name="​", value="데이터가 없습니다.", inline=False)
    for idx, row in enumerate(ranking, start=1):
        name = row["nick"] or row["name"]
        embed.add_field(name=f"{idx}위 - {name}", value=f"+{row['earned']}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=False)
    log_command(interaction, "/랭킹 월간")


@ranking_group.command(name="누적", description="보유 허니 기준 랭킹")
async def total_ranking(interaction: discord.Interaction):
    if not db.get_user(str(interaction.user.id)):
        await interaction.response.send_message(
            "먼저 /가입을 해주세요.", ephemeral=True
        )
        return
    ranking = db.get_total_ranking()
    embed = discord.Embed(title="누적 허니 랭킹", color=discord.Color.gold())
    if not ranking:
        embed.add_field(name="​", value="데이터가 없습니다.", inline=False)
    for idx, row in enumerate(ranking, start=1):
        name = row["nick"] or row["name"]
        embed.add_field(name=f"{idx}위 - {name}", value=str(row['honey']), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=False)
    log_command(interaction, "/랭킹 누적")


@app_commands.command(name="꽃뽑기", description="꽃 아이템을 뽑습니다")
async def flower_gacha(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    info = db.get_user(user_id)
    if not info:
        await interaction.response.send_message("먼저 /가입을 해주세요.", ephemeral=True)
        return
    if info["honey"] < 100:
        await interaction.response.send_message("허니가 부족합니다.", ephemeral=True)
        return
    db.add_honey(user_id, -100)
    total = sum(item["weight"] for item in FLOWER_ITEMS)
    r = random.uniform(0, total)
    cumulative = 0
    chosen = FLOWER_ITEMS[0]
    for item in FLOWER_ITEMS:
        cumulative += item["weight"]
        if r <= cumulative:
            chosen = item
            break
    result_text = apply_flower_effect(user_id, chosen)
    embed = discord.Embed(title=f"{chosen['name']} 획득!", color=discord.Color.gold())
    embed.add_field(name="등급", value=chosen.get("rarity", "?"), inline=False)
    embed.add_field(name="효과", value=result_text, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=False)
    log_command(interaction, "/꽃뽑기", chosen.get("name", ""))




bot.tree.add_command(greet_command)
bot.tree.add_command(join_command)
bot.tree.add_command(honey_command)
bot.tree.add_command(honey_group)
bot.tree.add_command(adventure_logs_command)
bot.tree.add_command(adventure)
bot.tree.add_command(flower_gacha)
bot.tree.add_command(ranking_group)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN 값이 설정되지 않았습니다. 환경 변수로 설정하거나 .env 파일을 사용하세요.")
    db.init_db()
    bot.run(TOKEN)
