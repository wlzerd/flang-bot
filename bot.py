import os
import time
import uuid
from dataclasses import dataclass
import random
import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

import db

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = "간단한 디스코드 봇"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 허니 모임 위한 그룹
honey_group = app_commands.Group(name="허니", description="허니 관련 명령")
# 모험 명령 그룹
adventure_group = app_commands.Group(name="모험", description="모험 관련 명령")
# 랭킹 명령 그룹
ranking_group = app_commands.Group(name="랭킹", description="랭킹 관련 명령")


@bot.tree.interaction_check
async def check_allowed_channel(interaction: discord.Interaction) -> bool:
    """Restrict command usage to the configured channel for the guild."""
    if interaction.guild is None:
        return True
    if interaction.command and interaction.command.name == "채널":
        return True
    allowed = db.get_allowed_channel(str(interaction.guild.id))
    if allowed and interaction.channel_id != int(allowed):
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


class AdventureConfirmView(discord.ui.View):
    def __init__(self, user_id: int, amount: int, success_p: float, fail_p: float, normal_p: float):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.amount = amount
        self.success_p = success_p
        self.fail_p = fail_p
        self.normal_p = normal_p

    @discord.ui.button(label="진행하기", style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("이 모험을 시작할 권한이 없습니다.", ephemeral=True)
            return
        info = db.get_user(str(self.user_id))
        if not info or info.get("honey", 0) < self.amount:
            await interaction.response.send_message("허니가 부족합니다.", ephemeral=True)
            return
        db.add_honey(str(self.user_id), -self.amount)
        roll = random.random() * 100
        if roll < self.success_p:
            db.add_honey(str(self.user_id), self.amount * 2)
            result_msg = f"모험에 성공했습니다! {self.amount * 2} 허니를 받았습니다."
            db.add_adventure_log(str(self.user_id), "성공", self.amount, self.amount)
        elif roll < self.success_p + self.fail_p:
            result_msg = f"모험에 실패했습니다... {self.amount} 허니를 잃었습니다."
            db.add_adventure_log(str(self.user_id), "실패", self.amount, -self.amount)
        else:
            db.add_honey(str(self.user_id), self.amount)
            result_msg = f"무난히 끝났습니다. {self.amount} 허니를 돌려받았습니다."
            db.add_adventure_log(str(self.user_id), "무난", self.amount, 0)
        await interaction.response.edit_message(content=result_msg, embed=None, view=None)
        self.stop()

    @discord.ui.button(label="취소하기", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("취소할 권한이 없습니다.", ephemeral=True)
            return
        await interaction.response.edit_message(content="모험이 취소되었습니다.", embed=None, view=None)
        self.stop()


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
        db.add_honey(session.user_id, 0.5)
        session.last_award = now


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    info = db.get_user(str(message.author.id))
    if info:
        db.add_honey(str(message.author.id), 1)
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
    embed.add_field(name="내 허니", value=str(info.get("honey", 0)), inline=True)
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


@adventure_group.command(name="진행", description="모험을 진행합니다")
@app_commands.describe(amount="사용할 허니 양")
async def adventure_random(
    interaction: discord.Interaction,
    amount: app_commands.Range[int, 200],
):
    user_id = str(interaction.user.id)
    info = db.get_user(user_id)
    if not info:
        await interaction.response.send_message(
            "먼저 /가입을 해주세요.", ephemeral=True
        )
        return

    if not info or info.get("honey", 0) < amount:
        await interaction.response.send_message("허니가 부족합니다.", ephemeral=True)
        return

    success_p, fail_p, normal_p = db.get_adventure_probabilities()

    embed = discord.Embed(title="모험 확률", color=discord.Color.gold())
    embed.add_field(name="성공", value=f"{success_p}%", inline=True)
    embed.add_field(name="실패", value=f"{fail_p}%", inline=True)
    embed.add_field(name="무난", value=f"{normal_p}%", inline=True)
    embed.set_footer(text=f"{amount} 허니를 사용합니다.")

    view = AdventureConfirmView(interaction.user.id, amount, success_p, fail_p, normal_p)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


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


@adventure_group.command(name="확률", description="관리자만 사용가능합니다 모험 확률을 설정합니다")
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


@app_commands.command(name="채널", description="봇 명령을 허용할 채널을 설정합니다")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel="명령을 사용할 채널")
async def set_channel_command(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not interaction.guild:
        await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
        return
    db.set_allowed_channel(str(interaction.guild.id), str(channel.id))
    await interaction.response.send_message(
        f"{channel.mention} 채널에서만 명령을 사용할 수 있습니다.", ephemeral=True
    )


bot.tree.add_command(greet_command)
bot.tree.add_command(join_command)
bot.tree.add_command(honey_command)
bot.tree.add_command(grant_honey)
bot.tree.add_command(honey_group)
bot.tree.add_command(adventure_logs_command)
bot.tree.add_command(adventure_group)
bot.tree.add_command(set_channel_command)
bot.tree.add_command(ranking_group)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN 값이 설정되지 않았습니다. 환경 변수로 설정하거나 .env 파일을 사용하세요.")
    db.init_db()
    bot.run(TOKEN)
