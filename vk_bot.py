import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from datetime import *
from config import BOT_TOKEN_VK
import sqlite3
#списки для будущей проверки названий приложений
vk_app_names = ['vk', 'вк', 'вконтакте']
tg_app_names = ['tg', 'telgram', 'телграм', 'телега', 'тг']
ds_app_names = ['ds', 'discord', 'дс', 'дискорд']
help_words = ['help', 'помощь', 'помоги', 'привет', 'начать', 'hi', 'hello']
vk_session = vk_api.VkApi(token=BOT_TOKEN_VK)
vk = vk_session.get_api()

# функция для отправления всех сообщений пользователю
def send_msg(user_id, some_text):
    vk_session.method("messages.send",
                      {"user_id": user_id, "message": some_text,
                       "random_id": 0})

# основная функция, отвечающая за все команды
def main():
    for event in VkLongPoll(vk_session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            msg = str(event.text.lower())
            user_id = event.user_id
            for words in help_words:
                if msg == words:
                    send_msg(user_id, 'Привет, ознакомиться со всеми командами можно с помощью /commands')
            if '/commands' in msg:
                commands(user_id)
            elif '/add' in msg:
                add(user_id)
            elif '/delete' in msg:
                delete(user_id)
            elif '/today' in msg:
                today(user_id)
            elif '/day' in msg:
                day(user_id)
# перечень функций
def commands(user_id):
    send_msg(user_id, 'Список команд:\n'
                   "/add - добавить событие\n"
                   "/today - посмотреть рассписание на сегодня\n"
                   "/day - посмотреть рассписание на date день\n"
                   "/delete - удалить событие")

# функция добавления
def add(user_id):
    send_msg(user_id, "Напишите событие в формате 'Событие; год.месяц.день; приложение для отправки (запись нескольких в формате: 'ds, vk')")
    spis = []
    response = vk.users.get(user_id=user_id)
    for element in response:
        user = str(element['last_name']) + ' ' + str(element['first_name'])
    for event in VkLongPoll(vk_session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            task_full = str(event.text.lower())
            task = str(task_full.split('; ')[0])
            app_names = ((task_full.split('; ')[2]).lower()).split(', ')
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
                    send_msg(user_id,
                        f'Напиши нормальное название мессенджера. Выбирай из этого {ds_app_names}, {tg_app_names}, {vk_app_names}')
            send_msg(user_id, 'Событие записано и добавлено')
            break

# функция вывода событий на сегодняшний день
def today(user_id):
    send_msg(user_id, "Расписание на сегодня:")
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()
    today_date = str(
        (datetime.now().date()).strftime("%Y.%m.%d"))
    for app in vk_app_names:
        response = vk.users.get(user_id=user_id)
        for element in response:
            user = str(element['last_name']) + ' ' + str(element['first_name'])
        tasks = cur.execute(
            f"""SELECT tasks FROM tasks_user WHERE date='{today_date}' AND app='{app}'""").fetchall()
        for task in tasks:
            send_msg(user_id, task)
    con.commit()
    con.close()

# функция вывода событий на сегодняшний день
def day(user_id):
        send_msg(user_id, "Введите дату в формате год.месяц.день, чтобы увидеть расписание на день")
        con = sqlite3.connect("db/things.db")
        cur = con.cursor()

        for event in VkLongPoll(vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                mes = str(event.text.lower())
                response = vk.users.get(user_id=user_id)
                # for element in response:
                #     user = str(element['last_name']) + ' ' + str(
                #         element['first_name'])
                for app in vk_app_names:
                    tasks = cur.execute(
                    f"""SELECT tasks FROM tasks_user WHERE date='{mes}' AND app='{app}'""").fetchall()
                    for task in tasks:
                        send_msg(user_id, task)
                con.commit()
                con.close()
                break

# функция удаления
def delete(user_id):
    date = ''
    send_msg(user_id,
             "Введите дату и название события в формате 'Название события; год.месяц.день', чтобы удалить событие")
    con = sqlite3.connect("db/things.db")
    cur = con.cursor()

    for event in VkLongPoll(vk_session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.from_user:
                need_task_and_date = str(event.text.lower()).split('; ')
                print(need_task_and_date)
                task, date = need_task_and_date[0], need_task_and_date[1]
                for app in vk_app_names:
                    cur.execute(
                        f"""DELETE from tasks_user where date='{date}' AND tasks='{task}' AND app='{app}'""").fetchall()
                send_msg(user_id, 'Событие удалено')
                send_msg(user_id, 'Теперь ваши планы на указанный день:')
                for app in vk_app_names:
                    tasks = cur.execute(
                        f"""SELECT tasks FROM tasks_user WHERE date='{date}' AND app='{app}'""").fetchall()
                    for task0 in tasks:
                        for task in task0:
                            task = task.split('; ')[0]
                            if task != '':
                                send_msg(user_id, task)
                con.commit()
                con.close()
                break

