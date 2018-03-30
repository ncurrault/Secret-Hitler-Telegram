import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

with open("API_key.txt", "r") as f:
    API_KEY = f.read()

bot = telegram.Bot(token=API_KEY)
updater = Updater(token=API_KEY)
dispatcher = updater.dispatcher
