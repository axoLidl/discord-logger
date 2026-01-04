import discord
from discord.ext import commands
import os
from datetime import datetime

# ───── НАСТРОЙКИ ─────
LOG_CATEGORY_NAME = "logs"

LOG_CHANNELS = {
    "messages": "logs-messages",
    "mod": "logs-mod",
    "server": "logs-server"
}

# ───── ИНТЕНТЫ ─────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ───── ФАЙЛЫ ─────
os.makedirs("logs", exist_ok=True)

def write_log(filename, text):
    with open(f"logs/{filename}.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] {text}\n")

# ───── ПОЛУЧЕНИЕ ЛОГ-КАНАЛА ─────
async def get_log_channel(guild, key):
    category = discord.utils.get(guild.categories, name=LOG_CATEGORY_NAME)
    if not category:
        category = await guild.create_category(LOG_CATEGORY_NAME)

    channel = discord.utils.get(category.text_channels, name=LOG_CHANNELS[key])
    if not channel:
        channel = await guild.create_text_channel(LOG_CHANNELS[key], category=category)

    return channel

# ───── ГОТОВ ─────
@bot.event
async def on_ready():
    print(f"Бот запущен: {bot.user}")

# ───── СООБЩЕНИЯ ─────

@bot.event
async def on_message_delete(message):
    if not message.guild or message.author.bot:
        return

    text = (
        f"Автор: {message.author}\n"
        f"Канал: #{message.channel}\n\n"
        f"Сообщение:\n{message.content}"
    )

    write_log("messages", f"Сообщение удалено | {message.author} | #{message.channel} | {message.content}")

    channel = await get_log_channel(message.guild, "messages")
    embed = discord.Embed(
        title="🗑 Сообщение удалено",
        description=text,
        color=discord.Color.red()
    )
    await channel.send(embed=embed)


@bot.event
async def on_message_edit(before, after):
    if not before.guild or before.author.bot:
        return
    if before.content == after.content:
        return

    text = (
        f"Автор: {before.author}\n"
        f"Канал: #{before.channel}\n\n"
        f"Было:\n{before.content}\n\n"
        f"Стало:\n{after.content}"
    )

    write_log(
        "messages",
        f"Сообщение отредактировано | {before.author} | #{before.channel} | "
        f"Было: {before.content} | Стало: {after.content}"
    )

    channel = await get_log_channel(before.guild, "messages")
    embed = discord.Embed(
        title="✏️ Сообщение отредактировано",
        description=text,
        color=discord.Color.orange()
    )
    await channel.send(embed=embed)

# ───── МОДЕРАЦИЯ ─────

@bot.event
async def on_member_ban(guild, user):
    text = f"Пользователь: {user}"

    write_log("mod", f"Пользователь заблокирован | {user}")

    channel = await get_log_channel(guild, "mod")
    embed = discord.Embed(
        title="🔨 Пользователь заблокирован",
        description=text,
        color=discord.Color.dark_red()
    )
    await channel.send(embed=embed)


@bot.event
async def on_member_unban(guild, user):
    text = f"Пользователь: {user}"

    write_log("mod", f"Пользователь разблокирован | {user}")

    channel = await get_log_channel(guild, "mod")
    embed = discord.Embed(
        title="♻️ Пользователь разблокирован",
        description=text,
        color=discord.Color.green()
    )
    await channel.send(embed=embed)


@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return

    added_roles = set(after.roles) - set(before.roles)
    removed_roles = set(before.roles) - set(after.roles)

    channel = await get_log_channel(after.guild, "mod")

    for role in added_roles:
        if role.is_default():
            continue

        text = f"Пользователь: {after}\nРоль: {role.name}"
        write_log("mod", f"Выдана роль | {after} | {role.name}")

        embed = discord.Embed(
            title="🛡 Выдана роль",
            description=text,
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)

    for role in removed_roles:
        if role.is_default():
            continue
    text = f"Пользователь: {after}\nРоль: {role.name}"
        write_log("mod", f"Снята роль | {after} | {role.name}")

        embed = discord.Embed(
            title="🛡 Снята роль",
            description=text,
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)

# ───── СЕРВЕР ─────

@bot.event
async def on_guild_channel_create(channel):
    text = f"Канал: {channel.name}"

    write_log("server", f"Канал создан | {channel.name}")

    log_channel = await get_log_channel(channel.guild, "server")
    embed = discord.Embed(
        title="➕ Канал создан",
        description=text,
        color=discord.Color.green()
    )
    await log_channel.send(embed=embed)


@bot.event
async def on_guild_channel_delete(channel):
    text = f"Канал: {channel.name}"

    write_log("server", f"Канал удалён | {channel.name}")

    log_channel = await get_log_channel(channel.guild, "server")
    embed = discord.Embed(
        title="➖ Канал удалён",
        description=text,
        color=discord.Color.red()
    )
    await log_channel.send(embed=embed)

# ───── ЗАПУСК ─────
bot.run(os.getenv("TOKEN"))