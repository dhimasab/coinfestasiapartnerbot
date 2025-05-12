import telebot
import json
import os
from dotenv import load_dotenv

# Load env dari file .env
load_dotenv()

# ✅ Buat file credentials.json kalau ada GOOGLE_CREDS_RAW dari Railway
if "GOOGLE_CREDS_RAW" in os.environ:
    with open("credentials.json", "w") as f:
        json.dump(json.loads(os.environ["GOOGLE_CREDS_RAW"]), f)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Validasi token
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan di environment variables!")

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Handler untuk menerima postingan dari channel
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'sticker'])
def forward_post_to_groups(message):
    try:
        with open('groups.json', 'r') as f:
            group_ids = json.load(f)
    except:
        group_ids = []

    for group_id in group_ids:
        try:
            bot.forward_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.message_id)
            print(f"✅ Berhasil forward ke group {group_id}")
        except Exception as e:
            print(f"❌ Gagal kirim ke {group_id}: {e}")

# ✅ Handler saat bot ditambahkan ke grup
@bot.my_chat_member_handler()
def auto_add_group(event):
    if event.new_chat_member.status in ['member', 'administrator']:
        chat_id = event.chat.id
        chat_name = event.chat.title or 'Unnamed Group'

        try:
            with open('groups.json', 'r') as f:
                group_ids = json.load(f)
        except:
            group_ids = []

        if chat_id not in group_ids:
            group_ids.append(chat_id)
            with open('groups.json', 'w') as f:
                json.dump(group_ids, f)
            print(f"🆕 Grup baru ditambahkan ke daftar: {chat_name} (ID: {chat_id})")

            # NANTI DI SINI kamu bisa tambahkan logika untuk nulis ke Google Sheets
        else:
            print(f"ℹ️ Grup {chat

