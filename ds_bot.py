import discord
import logging
import sqlite3
from datetime import *
from config import BOT_TOKEN_DS
from discord.ext import commands
import requests
# подключение
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
TOKEN = BOT_TOKEN_DS
# утверждение символа, начинающего команду
bot = commands.Bot(command_prefix='>')
client = discord.Client()
#списки для будущей проверки названий приложений
help_words = ['help', 'помощь', 'помоги']
vk_app_names = ['vk', 'вк', 'вконтакте']
tg_app_names = ['tg', 'telgram', 'телграм', 'телега', 'тг']
ds_app_names = ['ds', 'discord', 'дс', 'дискорд']

#обработка всех событий
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if not message.author.bot:
        if "кот" in message.content.lower():
            response = requests.get('https://api.thecatapi.com/v1/images/search')
            data = response.json()
            await message.channel.send(data[0]['url'])
        if "привет" in message.content.lower():
            await message.channel.send(f"Привет, {message.author.mention}")
        for word in help_words:
            if word in message.content.lower():
                await message.channel.send(f"Команды вызываются с помощью значка"
                                           f" >. Ознакомиться со всеми функциями"
                                           f" можно через >commands")

# перечень команд
@bot.command()
async def commands(ctx):
    await ctx.send('Список команд:\n'
        ">add - добавить событие\n"
        ">today - посмотреть расписание на сегодня\n"
        ">day - посмотреть расписание на date день\n"
        ">delete - удалить событие")

# команда добавления
@bot.command()
async def add(ctx):
    spis = []
    channel = ctx.channel
    await ctx.send("Напишите событие в формате 'Событие; год.месяц.день; приложение для отправки (запись нескольких в формате: 'ds, vk')")
    # проверка того, что отправленное сообщение от пользователя
    def check(mes):
        if not mes.author.bot:
            return mes.content and mes.channel == channel
    mes = await bot.wait_for(event='message', check=check)
    task_full = str(mes.content)
    task = str(task_full.split('; ')[0])
    app_names = ((task_full.split('; ')[2]).lower()).split(', ')
    user = str(mes.author)
    date = str(task_full.split('; ')[1])
    spis.append(task_full)
    for app_name in app_names:
        if app_name in ds_app_names or app_name in tg_app_names or app_name in vk_app_names:
            con = sqlite3.connect("db/things.db")
            cur = con.cursor()
            cur.execute(
                """INSERT INTO tasks_user (username, tasks, date, app) VALUES (?, ?, ?, ?)""",
                (user, task, date, app_name))
            con.commit()
            con.close()
        else:
            await ctx.send(
                     f'Напиши нормальное название мессенджера. Выбирай из этого {ds_app_names}, {tg_app_names}, {vk_app_names}')
    await ctx.send('Событие записано и добавлено')

# функция вывода событий на сегодняшний день
@bot.command()
async def today(ctx):
    await ctx.send("Расписание на сегодня:")
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    mes = await bot.wait_for(event='message')
    user = str(mes.author)
    today_date = str((datetime.now().date()).strftime("%Y.%m.%d"))
    for app in ds_app_names:
        tasks = cur.execute(f"""SELECT tasks FROM tasks_user WHERE date='{today_date}' AND app='{app}'""").fetchall()
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                await ctx.send(task)
    con.commit()
    con.close()

# функция вывода событий на сегодняшний день
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
    user = str(mes.author)
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

# команда удаления
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
            f"""DELETE from tasks_user where date='{date}' AND tasks='{task}'""").fetchall()
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
bot.run(TOKEN)
