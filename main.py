import time
import sqlite3
import tg_bot
import ds_b
import telegram
import discord
import config

TOKEN_TG = config.BOT_TOKEN_TG
TOKEN_DS = config.BOT_TOKEN_DS

ds_b.run()
tg_bot.main()
