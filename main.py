
import time
import sqlite3
import tg_bot
import ds_b
import telegram
import discord
from discord.ext import commands
import config


bot = commands.Bot(command_prefix='>')
TOKEN_TG = config.BOT_TOKEN_TG
TOKEN_DS = config.BOT_TOKEN_DS

ds_b.bot.run(TOKEN_DS)
tg_bot.main()
