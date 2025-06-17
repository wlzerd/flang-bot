import os
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')

description = "간단한 디스코드 봇"

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.tree.command(name="커맨드", description="샘플 커맨드")
async def slash_command(interaction: discord.Interaction):
    await interaction.response.send_message("안녕하세요!", ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN 환경변수가 설정되지 않았습니다.")
    bot.run(TOKEN)
