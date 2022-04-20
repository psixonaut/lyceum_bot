import os
import discord
import logging
import sqlite3
from datetime import *
from config import BOT_TOKEN_DS
from discord.ext import commands
from tg_bot import tg_app_names

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
TOKEN = BOT_TOKEN_DS
bot = commands.Bot(command_prefix='>')
client = discord.Client()
help_words = ['help', 'помощь', 'помоги']
good_mood = ['нормально', 'отлично', 'хорошо']
bad_mood = ['плохо', 'ужасно']
ds_app_names = ['ds', 'discord', 'дс', 'дискорд']


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if not message.author.bot:
        if "привет" in message.content.lower():
            await message.channel.send(f"Привет, {message.author.mention}")
        if 'fail' or 'error' or 'damage' or 'ошибка' in message.content.lower():
            await message.channel.send("I guess it's time to go out @everyone")
        for word in help_words:
            if word in message.content.lower():
                await message.channel.send(f"Команды вызываются с помощью значка"
                                           f" >. Ознакомиться со всеми функциями"
                                           f" можно через >commands")

@bot.command()
async def commands(ctx):
    await ctx.send('Список команд:\n'
        ">add - добавить событие\n"
        ">today - посмотреть рассписание на сегодня\n"
        ">day - посмотреть рассписание на date день\n"
        ">delete - удалить событие\n"
        ">change - изменить событие")


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
    if app_name in ds_app_names or tg_app_names:
        con = sqlite3.connect("db/things.db")
        cur = con.cursor()
        cur.execute(
                    """INSERT INTO tasks_user (username, tasks, date, app) VALUES (?, ?, ?, ?)""",
                    (user, task, date, app_name))
        con.commit()
        con.close()
        await channel.send('Событие записано и добавлено')
    else:
        await channel.send(f'Напиши нормальное название мессенджера. Выбирай из этого {ds_app_names}, {tg_app_names}')


@bot.command()
async def today(ctx):
    await ctx.send("Расписание на сегодня:")
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    today_date = str((datetime.now().date()).strftime("%Y.%m.%d"))
    for app in ds_app_names:
        tasks = cur.execute(f"""SELECT tasks FROM tasks_user WHERE date='{today_date}' AND app='{app}'""").fetchall()
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                await ctx.send(task)
    con.commit()
    con.close()


@bot.command()
async def day(ctx):
    await ctx.send("Введите дату в формате год.месяц.день, чтобы увидеть расписание на день")
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    channel = ctx.channel

    def check(mes):
        if not mes.author.bot:
            return mes.content and mes.channel == channel
    mes = await bot.wait_for(event='message', check=check)
    need_date = str(mes.content)
    for app in ds_app_names:
        tasks = cur.execute(
            f"""SELECT tasks FROM tasks_user WHERE date='{need_date}' AND app='{app}'""").fetchall()
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                await ctx.send(task)
    con.commit()
    con.close()


@bot.command()
async def delete(ctx):
    await ctx.send("Введите дату и название события в формате 'Название события; год.месяц.день', чтобы удалить событее")
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    channel = ctx.channel

    def check(mes):
        if not mes.author.bot:
            return mes.content and mes.channel == channel

    mes = await bot.wait_for(event='message', check=check)
    need_task_and_date = str(mes.content).split('; ')
    task, date = need_task_and_date[0], need_task_and_date[1]
    for app in ds_app_names:
        cur.execute(
            f"""DELETE from tasks_user where date='{date}' AND tasks='{task}' AND app='{app}'""").fetchall()
    await ctx.send('Событие удалено')
    await ctx.send('Теперь ваши планы на указанный день:')
    for app in ds_app_names:
        tasks = cur.execute(
                f"""SELECT tasks FROM tasks_user WHERE date='{date}' AND app='{app}'""").fetchall()
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                if task != '':
                    await ctx.send(task)
    con.commit()
    con.close()


def run():
    bot.run(TOKEN)
