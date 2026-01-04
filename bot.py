import discord
from discord.ext import commands
import os
from datetime import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CATEGORY_NAME = "logs"
LOG_CHANNELS = {
    "messages": "logs-messages",
    "mod": "logs-mod",
    "server": "logs-server"
}

os.makedirs("logs", exist_ok=True)

def write_log(filename, text):
    with open(f"logs/{filename}.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {text}\n")

async def get_log_channel(guild, key):
    category = discord.utils.get(guild.categories, name=LOG_CATEGORY_NAME)
    if not category:
        category = await guild.create_category(LOG_CATEGORY_NAME)

    channel = discord.utils.get(category.text_channels, name=LOG_CHANNELS[key])
    if not channel:
        channel = await guild.create_text_channel(LOG_CHANNELS[key], category=category)

    return channel

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

# 🗑 Удаление сообщений
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    text = f"Message deleted | {message.author} | #{message.channel} | {message.content}"
    write_log("messages", text)

    channel = await get_log_channel(message.guild, "messages")
    embed = discord.Embed(title="🗑 Message deleted", description=text, color=discord.Color.red())
    await channel.send(embed=embed)

# ✏️ Редактирование сообщений
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return

    text = f"Message edited | {before.author} | #{before.channel}\nBefore: {before.content}\nAfter: {after.content}"
    write_log("messages", text)

    channel = await get_log_channel(before.guild, "messages")
    embed = discord.Embed(title="✏️ Message edited", description=text, color=discord.Color.orange())
    await channel.send(embed=embed)

# 🔨 Баны
@bot.event
async def on_member_ban(guild, user):
    text = f"User banned: {user}"
    write_log("mod", text)

    channel = await get_log_channel(guild, "mod")
    await channel.send(embed=discord.Embed(title="🔨 Ban", description=text, color=discord.Color.dark_red()))

@bot.event
async def on_member_unban(guild, user):
    text = f"User unbanned: {user}"
    write_log("mod", text)

    channel = await get_log_channel(guild, "mod")
    await channel.send(embed=discord.Embed(title="♻️ Unban", description=text, color=discord.Color.green()))

# 🛡 Роли
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        added = set(after.roles) - set(before.roles)
        removed = set(before.roles) - set(after.roles)

        for role in added:
            text = f"Role added: {after} -> {role.name}"
            write_log("mod", text)
            channel = await get_log_channel(after.guild, "mod")
            await channel.send(embed=discord.Embed(title="🛡 Role added", description=text, color=discord.Color.blue()))

        for role in removed:
            text = f"Role removed: {after} -> {role.name}"
            write_log("mod", text)
            channel = await get_log_channel(after.guild, "mod")
            await channel.send(embed=discord.Embed(title="🛡 Role removed", description=text, color=discord.Color.blue()))

# ⚙️ Каналы
@bot.event
async def on_guild_channel_create(channel):
    text = f"Channel created: {channel.name}"
    write_log("server", text)

    log = await get_log_channel(channel.guild, "server")
    await log.send(embed=discord.Embed(title="➕ Channel created", description=text, color=discord.Color.green()))

@bot.event
async def on_guild_channel_delete(channel):
    text = f"Channel deleted: {channel.name}"
    write_log("server", text)

    log = await get_log_channel(channel.guild, "server")
    await log.send(embed=discord.Embed(title="➖ Channel deleted", description=text, color=discord.Color.red()))

bot.run(os.getenv("TOKEN"))