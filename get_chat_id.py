from telegram.ext import Updater, MessageHandler, Filters

from config import BOT_TOKEN

def handle_message(update, context):
    chat = update.effective_chat
    print(f"Grup: {chat.title}")
    print(f"Chat ID: {chat.id}")

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.all, handle_message))

print("Bot siap menangkap chat_id... kirim pesan di grup sekarang.")
updater.start_polling()
updater.idle()
