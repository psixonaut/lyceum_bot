from config import BOT_TOKEN_TG

import sqlite3
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler
from datetime import *
ds_app_names = ['ds', 'discord', 'дс', 'дискорд']
tg_app_names = ['tg', 'telgram', 'телграм', 'телега', 'тг']
vk_app_names = ['vk', 'вк', 'вконтакте']

reply_keyboard = [['/help', '/today']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = BOT_TOKEN_TG


def start(update, context):
    update.message.reply_text(
        f"Привет, {update.message.from_user.first_name}, я бот - планировщик. Вы можете записывать в меня свои планы",
        reply_markup=markup
    )


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def help(update, context):
    update.message.reply_text(
        "Напишите событие в форме"
        " '/add Название события; год.месяц.день; приложение для отправки', чтобы добавить событие\n"
        "/today - посмотреть рассписание на сегодня\n"
        "Введите дату в формате '/day год.месяц.день', чтобы увидеть рассписание на день\n"
        "Введите дату и название события в формате '/delete Название события, год.месяц.день', чтобы удалить событие\n")


def add(update, context):
    thing = str(update.message.text).lstrip('/add').strip().split(';')
    thing[0] = thing[0].replace(' ', '')
    if thing[2] in tg_app_names or thing[2] in ds_app_names or thing[2] in vk_app_names:
        con = sqlite3.connect("db/things.db")
        cur = con.cursor()
        cur.execute(
            """INSERT INTO tasks_user (username, tasks, date, app) VALUES (?, ?, ?, ?)""",
            (update.message.from_user.first_name, thing[0], thing[1], thing[2]))
        con.commit()
        con.close()
        update.message.reply_text(f"Событие успешно добавлено")
    else:
        print(f'Название мессенджера должно быть одним из этих {tg_app_names, ds_app_names, vk_app_names}.')


def today(update, context):
    update.message.reply_text(f"Рассписание на сегодня:")
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    today_date = str((datetime.now().date()).strftime("%Y.%m.%d"))
    for app in tg_app_names:
        tasks = cur.execute(f"""SELECT tasks FROM tasks_user WHERE date = '{today_date}' AND app = '{app}'""").fetchall()
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                update.message.reply_text(task)
        con.commit()
        con.close()


def day(update, context):
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    need_date = str(update.message.text).lstrip('/day').strip().replace(' ', '')
    for app in tg_app_names:
        tasks = cur.execute(
            f"""SELECT tasks FROM tasks_user WHERE date='{need_date}' AND app='{app}'""").fetchall()
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                update.message.reply_text(task)
        con.commit()
        con.close()


def delete(update, context):
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    need_task_and_date = str(update.message.text).lstrip('/delete').strip().split(',')
    need_task_and_date[0] = need_task_and_date[0].replace(' ', '')
    task, date = need_task_and_date[0], need_task_and_date[1]
    for app in tg_app_names:
        cur.execute(
            f"""DELETE from tasks_user where date='{date}' AND tasks='{task}' AND app='{app}'""").fetchall()
        update.message.reply_text('Событие удалено')
        tasks = cur.execute(
            f"""SELECT tasks FROM tasks_user WHERE date='{date}' and app='{app}'""").fetchall()
        update.message.reply_text('Теперь ваши планы на день:')
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                update.message.reply_text(task)
        con.commit()
        con.close()


def change(update, context):
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()


def start_work():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("today", today))
    dp.add_handler(CommandHandler("day", day))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("change", change))
    updater.start_polling()

    updater.idle()
