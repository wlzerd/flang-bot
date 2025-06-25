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

# Adventure level settings
ADVENTURE_LEVELS = [
    {
        "name": "새싹들판",
        "success": 90,
        "reward": 100,
        "banner": "banner/Lv1.gif",
        "success_desc": "> 플로비가 부드러운 바람을 따라 들판을 누비다가 . . .",
        "fail_desc": "> 플로비가 나비를 따라가다 길을 잃어버리면서 . . .",
    },
    {
        "name": "튤립정원",
        "success": 75,
        "reward": 300,
        "banner": "banner/Lv2.gif",
        "success_desc": "> 플로비가 알록달록한 튤립 사이를 누비다가 . . .",
        "fail_desc": "> 플로비가 튤립 속에 숨은 벌레를 보고 깜짝 놀라 . . .",
    },
    {
        "name": "라벤더숲",
        "success": 60,
        "reward": 500,
        "banner": "banner/Lv3.gif",
        "success_desc": "> 플로비가 보라빛 향기에 이끌려 숲을 탐험하다가 . . .",
        "fail_desc": "> 플로비가 숲속 깊이 들어갔다가 길을 잃고 . . .",
    },
    {
        "name": "가시덤불",
        "success": 45,
        "reward": 700,
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
    },
    {
        "name": "민들레",
        "rarity": "커먼",
        "weight": 60,
        "effect": "adventure_success_bonus",
        "value": 5,
    },
    {
        "name": "코스모스",
        "rarity": "커먼",
        "weight": 60,
        "effect": "chat_double",
        "duration": 1800,
    },
    {
        "name": "튤립",
        "rarity": "에픽",
        "weight": 25,
        "effect": "voice_double",
        "duration": 3600,
    },
    {
        "name": "장미",
        "rarity": "에픽",
        "weight": 25,
        "effect": "gift_bonus",
        "duration": 3600,
    },
    {
        "name": "해바라기",
        "rarity": "에픽",
        "weight": 25,
        "effect": "cooldown_half",
        "duration": 3600,
    },
    {
        "name": "라벤더",
        "rarity": "레어",
        "weight": 10,
        "effect": "adventure_reward_bonus",
        "duration": 86400,
        "value": 0.5,
    },
    {
        "name": "수국",
        "rarity": "레어",
        "weight": 10,
        "effect": "free_adventure",
        "duration": 86400,
    },
    {
        "name": "동백꽃",
        "rarity": "레어",
        "weight": 10,
        "effect": "gift_cashback",
        "duration": 3600,
    },
    {
        "name": "벚꽃",
        "rarity": "전설",
        "weight": 5,
        "effect": "all_honey_double",
        "duration": 86400,
    },
    {
        "name": "달맞이꽃",
        "rarity": "전설",
        "weight": 5,
        "effect": "adventure_auto_success",
    },
    {
        "name": "별꽃",
        "rarity": "전설",
        "weight": 5,
        "effect": "honey_plus",
        "value": 500,
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
    now = int(time.time())
    effect = item.get("effect")
    if effect == "honey_plus":
        db.add_honey(user_id, item.get("value", 0))
        return f"{item['name']}을(를) 얻어 {item.get('value', 0)} 허니를 획득했습니다!"
    if effect == "adventure_auto_success":
        level = ADVENTURE_LEVELS[-1]
        db.add_honey(user_id, level["reward"])
        db.add_adventure_log(user_id, "성공", level["reward"], level["reward"])
        return f"{item['name']}의 힘으로 {level['name']} 모험을 성공해 {level['reward']} 허니를 얻었습니다!"
    db.add_effect(user_id, effect, 0, {"value": item.get("value")})
    return f"{item['name']} 효과가 영구적으로 적용됩니다!"


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


@app_commands.command(name="인사", description="인사 메시지")
async def greet_command(interaction: discord.Interaction):
    await interaction.response.send_message("안녕하세요!", ephemeral=True)


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
    )
    await interaction.response.send_message(
        f"{user.name}님의 정보가 저장되었습니다.", ephemeral=True
    )


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
    embed.add_field(name="\u200b", value=f"[{str(info.get('honey', 0))}] 허니를 보유하고 있습니다!", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=False)


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


@app_commands.command(name="지급", description=" 관리자 권한을 가진 사용자만 사용가능합니다. 특정 사유로 허니를 지급합니다")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    user="허니를 지급할 사용자",
    amount="지급할 허니 양",
    reason="지급 사유",
)
async def grant_honey(
    interaction: discord.Interaction,
    user: discord.Member,
    amount: app_commands.Range[int, 1],
    reason: str,
):
    if not db.get_user(str(user.id)):
        await interaction.response.send_message(
            "해당 사용자가 /가입을 하지 않았습니다.", ephemeral=True
        )
        return

    db.add_honey(str(user.id), amount)

    embed = discord.Embed(color=discord.Color.gold())
    embed.add_field(
        name="\u200b",
        value=f"{reason}로 인해 {amount} 허니가 지급됬어요",
        inline=False,
    )
    try:
        await user.send(embed=embed)
    except Exception:
        pass

    await interaction.response.send_message("허니가 지급되었습니다.", ephemeral=True)



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


@app_commands.command(name="모험확률", description="관리자만 사용가능합니다 모험 확률을 설정합니다")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(success="성공 확률", fail="실패 확률", normal="무난한 확률")
async def set_adventure_prob(
    interaction: discord.Interaction,
    success: app_commands.Range[float, 0, 100],
    fail: app_commands.Range[float, 0, 100],
    normal: app_commands.Range[float, 0, 100],
):
    total = success + fail + normal
    if abs(total - 100) > 1e-6:
        await interaction.response.send_message("세 확률의 합은 100이어야 합니다.", ephemeral=True)
        return
    db.set_adventure_probabilities(success, fail, normal)
    await interaction.response.send_message("모험 확률이 업데이트되었습니다.", ephemeral=False)


@app_commands.command(name="채널", description="봇 명령을 허용할 채널을 추가합니다")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel="명령을 사용할 채널")
async def set_channel_command(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not interaction.guild:
        await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
        return
    db.add_allowed_channel(str(interaction.guild.id), str(channel.id))
    await interaction.response.send_message(
        f"{channel.mention} 채널이 명령 허용 목록에 추가되었습니다.", ephemeral=True
    )


bot.tree.add_command(greet_command)
bot.tree.add_command(join_command)
bot.tree.add_command(honey_command)
bot.tree.add_command(grant_honey)
bot.tree.add_command(honey_group)
bot.tree.add_command(adventure_logs_command)
bot.tree.add_command(adventure)
bot.tree.add_command(flower_gacha)
bot.tree.add_command(set_adventure_prob)
bot.tree.add_command(set_channel_command)
bot.tree.add_command(ranking_group)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN 값이 설정되지 않았습니다. 환경 변수로 설정하거나 .env 파일을 사용하세요.")
    db.init_db()
    bot.run(TOKEN)
