import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import db

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = "간단한 디스코드 봇"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


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
    nick = getattr(user, "nick", None)
    db.add_or_update_user(
        str(user.id),
        user.name,
        user.discriminator,
        avatar_url,
        nick,
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

    message = (
        f"ID: {info['user_id']}\n"
        f"이름: {info['name']}#{info['discriminator']}\n"
    )
    if info.get("nick"):
        message += f"닉네임: {info['nick']}\n"
    if info.get("avatar_url"):
        message += f"아바타: {info['avatar_url']}"
    await interaction.response.send_message(message, ephemeral=True)


bot.tree.add_command(greet_command)
bot.tree.add_command(join_command)
bot.tree.add_command(honey_command)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN 값이 설정되지 않았습니다. 환경 변수로 설정하거나 .env 파일을 사용하세요.")
    db.init_db()
    bot.run(TOKEN)
