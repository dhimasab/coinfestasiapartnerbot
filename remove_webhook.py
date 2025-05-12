import telebot
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()
print("✅ Webhook berhasil dihapus")
