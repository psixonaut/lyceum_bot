from config import BOT_TOKEN_TG

import sqlite3
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler
from datetime import *
ds_app_names = ['ds', 'discord', 'дс', 'дискорд']
tg_app_names = ['tg', 'telgram', 'телграм', 'телега', 'тг']

#клавиатура с ответами
reply_keyboard = [['/help', '/today']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


#логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = BOT_TOKEN_TG


#старт программы
def start(update, context):
    update.message.reply_text(
        f"Привет, {update.message.from_user.first_name}, я бот - планировщик. Вы можете записывать в меня свои планы",
        reply_markup=markup
    )


#закрыть клавиатуру
def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


#помощь
def help(update, context):
    update.message.reply_text(
        "Напишите событие в форме"
        " '/add Название событие; год.месяц.день; приложение для отправки', чтобы добавить событие\n"
        "/today - посмотреть расписание на сегодня\n"
        "Введите дату в формате '/day год.месяц.день', чтобы увидеть расписание на день\n"
        "Введите дату и название событие в формате '/delete Название событие; год.месяц.день', чтобы удалить событие\n")


#добавление события
def add(update, context):
    thing = str(update.message.text).lstrip('/add').strip().split(';')
    thing[0] = thing[0].strip()
    thing[2] = 'tg'
    thing[1] = thing[1].replace(' ', '')
    if thing[2] in tg_app_names or ds_app_names:
        con = sqlite3.connect("db/things.db")
        cur = con.cursor()
        cur.execute(
            """INSERT INTO tasks_user (username, tasks, date, app) VALUES (?, ?, ?, ?)""",
            (update.message.from_user.first_name, thing[0], thing[1], thing[2]))
        con.commit()
        con.close()
        update.message.reply_text(f"Событие успешно добавлено")
    else:
        update.message.reply_text(f'Название мессенджера должно быть одним из этих {tg_app_names, ds_app_names}.')


#вывод событий на сегодня
def today(update, context):
    update.message.reply_text(f"Расписание на сегодня:")
    today_date = str((datetime.now().date()).strftime("%Y.%m.%d"))
    for app in tg_app_names:
        con = sqlite3.connect("db/things.db")
        cur = con.cursor()
        tasks = cur.execute(f"""SELECT tasks FROM tasks_user WHERE date='{today_date}' AND app='{app}' AND
                                username='{update.message.from_user.first_name}'""").fetchall()
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                update.message.reply_text(task)
        con.commit()
        con.close()


#выводит события на определённый день
def day(update, context):
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    need_date = str(update.message.text).lstrip('/day').strip().replace(' ', '')
    for app in tg_app_names:
        tasks = cur.execute(
            f"""SELECT tasks FROM tasks_user WHERE date='{need_date}' AND app='{app}'
                        AND username = '{update.message.from_user.first_name}'""").fetchall()
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                update.message.reply_text(task)
    con.commit()
    con.close()


#удаляет событие
def delete(update, context):
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    need_task_and_date = str(update.message.text).lstrip('/delete').strip().split(';')
    need_task_and_date[0] = need_task_and_date[0].replace(' ', '')
    task, date = need_task_and_date[0], need_task_and_date[1]
    for app in tg_app_names:
        cur.execute(
            f"""DELETE from tasks_user where date='{date}' AND tasks='{task}' AND app='{app}'
                        AND username = '{update.message.from_user.first_name}'""").fetchall()
        update.message.reply_text('Событие удалено')
        tasks = cur.execute(
            f"""SELECT tasks FROM tasks_user WHERE date='{date}' and app='{app}'
                        AND username = '{update.message.from_user.first_name}'""").fetchall()
        update.message.reply_text('Теперь ваши планы на день:')
        for task0 in tasks:
            for task in task0:
                task = task.split('; ')[0]
                update.message.reply_text(task)
        con.commit()
        con.close()


#запуск бота
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
    updater.start_polling()
    updater.idle()


#кодовое слово для конфига - token_key, ссылка на перевод - https://planetcalc.ru/2468/?text=BOT_TOKEN_TG%20%3D%20'5389484482%3AAAElsVC7-gy4-Xi8jRevVXwgTT-VF0lMIYk'%0ABOT_TOKEN_DS%20%3D%20'OTYzOTIxNzQ4NTkwNDYwOTU4.YldIFQ.QP9iEuoRW9aCsR03LTJjIWnuirA'%0ABOT_TOKEN_VK%20%3D%20'6983e672abcad7301d719931efbf0e2144efe94c0474b5ca56e95656677234b57faad945d10a61146cdc3'%0Agroup_id%20%3D%20'212033635'&key=token_key&transform=c&method=ROT1&aselector=english
if __name__ == '__main__':
    main()
