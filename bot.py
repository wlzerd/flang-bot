import os
import time
import uuid
from dataclasses import dataclass

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


@dataclass
class VoiceSession:
    session_id: str
    user_id: str
    last_award: float


voice_sessions: dict[int, VoiceSession] = {}


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
    now = time.time()
    for session in list(voice_sessions.values()):
        db.add_honey(session.user_id, 1)
        session.last_award = now


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    await ensure_user_record(message.author, message.guild)
    db.add_honey(str(message.author.id), 1)
    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel is None and after.channel is not None:
        await ensure_user_record(member, after.channel.guild)
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
    author_name = display_name if not discriminator else f"{display_name}#{discriminator}"
    embed.set_author(
        name=author_name,
        icon_url=avatar_url,
    )
    embed.add_field(name="내 허니", value=str(info.get("honey", 0)), inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


bot.tree.add_command(greet_command)
bot.tree.add_command(join_command)
bot.tree.add_command(honey_command)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN 값이 설정되지 않았습니다. 환경 변수로 설정하거나 .env 파일을 사용하세요.")
    db.init_db()
    bot.run(TOKEN)
