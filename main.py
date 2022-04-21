from tg_bot import *
import ds_b
import config


TOKEN_TG = config.BOT_TOKEN_TG
TOKEN_DS = config.BOT_TOKEN_DS


def main():
    updater = Updater(TOKEN_TG)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("today", today))
    dp.add_handler(CommandHandler("day", day))
    dp.add_handler(CommandHandler("delete", delete))
    updater.start_polling()
    ds_b.bot.run(TOKEN_DS)
    updater.idle()




if __name__ == '__main__':
    main()
