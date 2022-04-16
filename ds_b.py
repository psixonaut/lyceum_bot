import os
import discord
import logging
import sqlite3
from datetime import *
from config import BOT_TOKEN_DS
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
TOKEN = BOT_TOKEN_DS
bot = commands.Bot(command_prefix='>')
client = discord.Client()
help_words = ['help', 'помощь', 'помоги']
good_mood = ['нормально', 'отлично', 'хорошо']
bad_mood = ['плохо', 'ужасно']

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if not message.author.bot:
        if "привет" in message.content.lower():
            await message.channel.send(f"Привет, {message.author.mention}")
        for word in help_words:
            if word in message.content.lower():
                await message.channel.send(f"Команды вызываются с помощью значка"
                                           f" >. Ознакомиться со всеми функциями"
                                           f" можно через >commands")


@bot.command()
async def dialog(ctx):
    await ctx.send('Давайте поговорим')
    await ctx.send('Как дела?')
    await bot.wait_for('message')
    await ctx.send('Ого. Ну в любом случае желаю тебе удачи')
    await ctx.send('Отлично поболтали, спасибо')

@bot.command()
async def commands(ctx):
    await ctx.send('Список команд:\n'
        ">add - добавить событие\n"
        ">today - посмотреть рассписание на сегодня\n"
        ">day - посмотреть рассписание на date день\n"
        ">delete - удалить событие\n"
        ">change - изменить событие\n"
        ">dialog - немного поболтать с ботом")


@bot.command()
async def add(ctx):
    spis = []
    channel = ctx.channel
    await ctx.send("Напишите событие в формате 'Событие; год.месяц.день; приложение для отправки")
    def check(mes):
        if not mes.author.bot:
            return mes.content and mes.channel == channel
    mes = await bot.wait_for(event='message', check=check)
    task_full = str(mes.content)
    task = str(task_full.split('; ')[0])
    app_name = (task_full.split('; ')[2]).lower()
    user = str(mes.author)
    date = str(task_full.split('; ')[1])
    spis.append(task_full)
    con = sqlite3.connect("data/things.db")
    cur = con.cursor()
    cur.execute(
                """INSERT INTO tasks_user (username, tasks, date, app) VALUES (?, ?, ?, ?)""",
                (user, task, date, app_name))
    con.commit()
    con.close()
    await channel.send('Событие записано и добавлено')


@bot.command()
async def today(ctx):
    await ctx.send("Расписание на сегодня:")
    con = sqlite3.connect("data/things.db")
    cur = con.cursor()
    today_date = str((datetime.now().date()).strftime("%Y.%m.%d"))
    tasks = cur.execute(f"""SELECT tasks FROM tasks_user WHERE date='{today_date}'""").fetchall()
    for task0 in tasks:
        for task in task0:
            task = task.split('; ')[0]
            await ctx.send(task)
    con.commit()
    con.close()


@bot.command()
async def day(ctx):
    await ctx.send("Введите дату в формате год.месяц.день, чтобы увидеть расписание на день")
    con = sqlite3.connect("data/things.db")
    cur = con.cursor()
    channel = ctx.channel

    def check(mes):
        if not mes.author.bot:
            return mes.content and mes.channel == channel
    mes = await bot.wait_for(event='message', check=check)
    need_date = str(mes.content)
    tasks = cur.execute(
        f"""SELECT tasks FROM tasks_user WHERE date='{need_date}'""").fetchall()
    for task0 in tasks:
        for task in task0:
            task = task.split('; ')[0]
            await ctx.send(task)
    con.commit()
    con.close()


@bot.command()
async def delete(ctx):
    await ctx.send("Введите дату и название события в формате 'Название события, год.месяц.день', чтобы удалить событее")
    con = sqlite3.connect("data/things.db")
    cur = con.cursor()
    channel = ctx.channel

    def check(mes):
        if not mes.author.bot:
            return mes.content and mes.channel == channel

    mes = await bot.wait_for(event='message', check=check)
    need_task_and_date = str(mes.content).split(', ')
    task, date = need_task_and_date[0], need_task_and_date[1]
    cur.execute(
        f"""DELETE from tasks_user where date='{date}' AND tasks='{task}'""").fetchall()
    await ctx.send('Событие удалено')
    tasks = cur.execute(
        f"""SELECT tasks FROM tasks_user WHERE date='{date}'""").fetchall()
    await ctx.send('Теперь ваши планы на день:')
    for task0 in tasks:
        for task in task0:
            task = task.split('; ')[0]
            await ctx.send(task)
    con.commit()
    con.close()


@bot.command()
async def change(ctx):
    await ctx.send(
        "Введите дату и название события, которое хотите изменить, в формате 'Название события, год.месяц.день'")
    con = sqlite3.connect("data/things.db")
    cur = con.cursor()
    channel = ctx.channel
    def check(mes):
        if not mes.author.bot:
            return mes.content and mes.channel == channel

    mes = await bot.wait_for(event='message', check=check)
    need_task_and_date = str(mes.content).split(', ')
    task, date = need_task_and_date[0], need_task_and_date[1]
    await ctx.send(embed=discord.Embed(title='Что вы хотите изменить?'),
                   components=[Button(style=ButtonStyle.blue, label='дату'),
                               Button(style=ButtonStyle.blue, label='событие'),
                               Button(style=ButtonStyle.blue, label='приложение')])
    ans = await bot.wait_for('button_click')
    need_to_change = ans.component.label
    if need_to_change == 'дату':
        await ctx.send(
            "Введите желаемую дату в формате: год.месяц.день")
        cur.execute(
                    f"""UPDATE tasks_user SET date = '' WHERE date = '{date}' AND tasks = '{task}'""")
    elif need_to_change == 'событие':
        await ctx.send(
            "Введите желаемое событие")
    elif need_to_change == 'приложение':
        await ctx.send(
            "Введите желаемое приложение")
bot.run(TOKEN)