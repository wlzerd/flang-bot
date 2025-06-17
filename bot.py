import os
import json
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = "간단한 디스코드 봇"

DATA_FILE = "users.json"

def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_data(data: dict):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

intents = discord.Intents.default()

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


cmd_group = app_commands.Group(name="커맨드", description="샘플 커맨드 그룹")


@cmd_group.command(name="인사", description="인사 메시지")
async def greet_command(interaction: discord.Interaction):
    await interaction.response.send_message("안녕하세요!", ephemeral=True)


@cmd_group.command(name="가입", description="사용자 정보를 저장합니다")
async def join_command(interaction: discord.Interaction):
    user = interaction.user
    data = load_user_data()
    data[str(user.id)] = {
        "name": user.name,
        "discriminator": user.discriminator,
    }
    save_user_data(data)
    await interaction.response.send_message(
        f"{user.name}님의 정보가 저장되었습니다.", ephemeral=True
    )


bot.tree.add_command(cmd_group)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN 값이 설정되지 않았습니다. 환경 변수로 설정하거나 .env 파일을 사용하세요.")
    bot.run(TOKEN)
