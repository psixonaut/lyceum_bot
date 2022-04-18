from config import BOT_TOKEN_TG

import sqlite3
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler
from datetime import *

reply_keyboard = [['/help', '/add', '/change'],
                  ['/today', '/day', '/delete']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = BOT_TOKEN_TG


def start(update, context):
    update.message.reply_text(
        "Я бот - планировщик. Вы можете записывать в меня свои планы",
        reply_markup=markup
    )


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def help(update, context):
    update.message.reply_text(
        "/add - Напишите событее в форме 'Название события; год.месяц.день; приложение для отправки', чтобы добавить событее\n"
        "/today - посмотреть рассписание на сегодня\n"
        "/day - Введите дату в формате год.месяц.день, чтобы увидеть рассписание на день\n"
        "/delete - Введите дату и название события в формате 'Название события, год.месяц.день', чтобы удалить событее\n"
        "/change - изменить событее\n")


def add(update, context):
    thing = str(update.message.text).lstrip('/add').strip().split(';')
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    cur.execute(
        """INSERT INTO tasks_user (username, tasks, date, app) VALUES (?, ?, ?, ?)""",
        (update.message.from_user.first_name, thing[0], thing[1], thing[2]))
    con.commit()
    con.close()



def today(update, context):
    update.message.reply_text(f"Рассписание на сегодня:")
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    today_date = str((datetime.now().date()).strftime("%Y.%m.%d"))
    tasks = cur.execute(f"""SELECT tasks FROM tasks_user WHERE date='{today_date}'""").fetchall()
    for task0 in tasks:
        for task in task0:
            task = task.split('; ')[0]
            update.message.reply_text(task)
    con.commit()
    con.close()


def day(update, context):
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    need_date = str(update.message.text).lstrip('/day').strip()
    tasks = cur.execute(
        f"""SELECT tasks FROM tasks_user WHERE date='{need_date}'""").fetchall()
    for task0 in tasks:
        for task in task0:
            task = task.split('; ')[0]
            update.message.reply_text(task)
    con.commit()
    con.close()


def delete(update, context):
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    need_task_and_date = str(update.message.text).lstrip('/delete').strip().split(', ')
    task, date = need_task_and_date[0], need_task_and_date[1]
    cur.execute(
        f"""DELETE from tasks_user where date='{date}' AND tasks='{task}'""").fetchall()
    update.message.reply_text('Событие удалено')
    tasks = cur.execute(
        f"""SELECT tasks FROM tasks_user WHERE date='{date}'""").fetchall()
    update.message.reply_text('Теперь ваши планы на день:')
    for task0 in tasks:
        for task in task0:
            task = task.split('; ')[0]
            update.message.reply_text(task)
    con.commit()
    con.close()


# def change(update, context):
#     update.message.reply_text(
#         "Введите дату и название события в формате 'Название события, год.месяц.день' и новое событее в формате"
#         " 'Название события; год.месяц.день' для изменения")
#     thing = yield context.split(';')


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("today", today))
    dp.add_handler(CommandHandler("day", day))
    dp.add_handler(CommandHandler("delete", delete))
    # dp.add_handler(CommandHandler("change", change))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
