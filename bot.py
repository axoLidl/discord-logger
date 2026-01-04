import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user}")

@bot.event
async def on_message_delete(message):
    if not config["logs"]["messages"]:
        return
    if message.author.bot:
        return

    print(
        f"[DELETE] "
        f"Автор: {message.author} | "
        f"Канал: {message.channel} | "
        f"Текст: {message.content}"
    )

bot.run(os.getenv("TOKEN"))