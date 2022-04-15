import os
import discord
import logging
import sqlite3
from config import BOT_TOKEN_DS
from discord.ext import commands
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
TOKEN = BOT_TOKEN_DS
bot = commands.Bot(command_prefix='>')
client = discord.Client()
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if not message.author.bot:
        if "привет" in message.content.lower():
            await message.channel.send(f"Привет, {message.author.mention}")


@bot.command()
async def hello(ctx):
    await ctx.send('hello, new friend')

@bot.command()
async def dialog(ctx):
    await ctx.send('Давайте поговорим')
    if not ctx.author.bot:
        if "как дела" in str(ctx).lower():
            await ctx.channel.send("Всё здорово, спасибо")
        else:
            await ctx.channel.send("Не можем разобрать, введите ещё раз")

@bot.command()
async def commands(ctx):
    await ctx.send('Список команд:'
        "/add - добавить событие"
        "/today - посмотреть рассписание на сегодня"
        "/day - посмотреть рассписание на date день"
        "/delete - удалить событее"
        "/change - изменить событее")


@bot.command()
async def add(ctx):
    channel = ctx.channel
    await ctx.send("Напишите событие в форме 'Название события; год.месяц.день.время; дополнительные сведенья'")
    def check(mes):
        return mes.content and mes.channel == channel
    mes = await bot.wait_for('message', check=check)
    task_to_bd = str(mes.content)
    print(task_to_bd)
    con = sqlite3.connect("data/things.db")
    cur = con.cursor()
    cur.execute(
                """INSERT INTO tasks_user (tasks) VALUES (?)""",
                (task_to_bd))
    con.commit()
    con.close()
    await channel.send('Событие записано и добавлено')


@bot.command()
async def today(ctx):
    await ctx.send("Расписание на сегодня:")
@bot.command()
async def day(ctx):
    await ctx.send("Введите дату в формате год.месяц.день, чтобы увидеть рассписание на день")
@bot.command()
async def delete(ctx):
    await ctx.send("Введите дату и название события в формате 'Название события, год.месяц.день', чтобы удалить событее")
@bot.command()
async def change(ctx):
    await ctx.send("Введите дату и название события в формате 'Название события, год.месяц.день' и новое событее в формате"
        "'Название события; год.месяц.день.время; дополнительные сведенья' для изменения")
bot.run(TOKEN)