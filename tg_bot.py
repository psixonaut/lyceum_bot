from config import BOT_TOKEN_TG

import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

reply_keyboard = [['/address', '/phone'],
                  ['/site', '/work_time']]

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
        "/add - добавить событее"
        "/today - посмотреть рассписание на сегодня"
        "/day - посмотреть рассписание на date день"
        "/delete - удалить событее"
        "/change - изменить событее")


def add(update, context):
    update.message.reply_text(
        "Напишите событее в форме 'Название события; год.месяц.день.время; дополнительные сведенья'")


def today(update, context):
    update.message.reply_text("Рассписание на сегодня:")


def day(update, context):
    update.message.reply_text(
        "Введите дату в формате год.месяц.день, чтобы увидеть рассписание на день")


def delete(update, context):
    update.message.reply_text(
        "Введите дату и название события в формате 'Название события, год.месяц.день', чтобы удалить событее")


def change(update, context):
    update.message.reply_text(
        "Введите дату и название события в формате 'Название события, год.месяц.день' и новое событее в формате"
        "'Название события; год.месяц.день.время; дополнительные сведенья' для изменения")


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("today", today))
    dp.add_handler(CommandHandler("day", day))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("change", change))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
