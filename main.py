import tg_bot
import vk_bot
from tg_bot import *
from vk_bot import *
import ds_b
import config
from threading import Thread


TOKEN_TG = config.BOT_TOKEN_TG
TOKEN_DS = config.BOT_TOKEN_DS

#Создаём функции с запуском телеграмм и вк ботов
def tg():
    tg_bot.main()


def vk():
    vk_bot.main()

    
#делаем функции асинхронными 
th1 = Thread(target=tg)
th2 = Thread(target=vk)


#запускаем функции
th1.start()
th2.start()
ds_bot.bot.run(TOKEN_DS)
