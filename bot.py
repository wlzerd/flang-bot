import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

description = "간단한 디스코드 봇"

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


@bot.tree.command(name="커맨드", description="샘플 커맨드")
async def slash_command(interaction: discord.Interaction):
    await interaction.response.send_message("안녕하세요!", ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN 값이 설정되지 않았습니다. 환경 변수로 설정하거나 .env 파일을 사용하세요.")
    bot.run(TOKEN)
