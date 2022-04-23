import vk_bot
from tg_bot import *
from vk_bot import *
import ds_b
import config
from threading import Thread


TOKEN_TG = config.BOT_TOKEN_TG
TOKEN_DS = config.BOT_TOKEN_DS


def tg():
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
    updater.idle()


def vk():
    vk_bot.main()


th1 = Thread(target=tg)
th2 = Thread(target=vk)


th1.start()
th2.start()
ds_b.bot.run(TOKEN_DS)
