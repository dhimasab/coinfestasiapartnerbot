import telebot
import json
import os
from dotenv import load_dotenv
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan di environment variables!")
if not SHEET_ID:
    raise ValueError("SHEET_ID tidak ditemukan di environment variables!")

# Setup Google Sheets access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_path = "/tmp/google-creds.json"

# Railway injects GOOGLE_CREDS_RAW sebagai env string
google_creds_raw = os.getenv("GOOGLE_CREDS_RAW")
if not google_creds_raw:
    raise ValueError("GOOGLE_CREDS_RAW tidak ditemukan di environment variables!")

with open(creds_path, "w") as f:
    f.write(google_creds_raw)

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# Init bot
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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open('groups.json', 'r') as f:
                group_ids = json.load(f)
        except:
            group_ids = []

        if chat_id not in group_ids:
            # Tambahkan ke JSON lokal
            group_ids.append(chat_id)
            with open('groups.json', 'w') as f:
                json.dump(group_ids, f)

            # Tambahkan ke Google Sheet
            sheet.append_row([str(chat_id), chat_name, timestamp])
            print(f"🆕 Grup baru ditambahkan: {chat_name} (ID: {chat_id})")
        else:
            print(f"ℹ️ Grup sudah ada: {chat_name} (ID: {chat_id})")

# Start bot
print("🤖 Bot aktif... Menunggu pesan dari channel atau event grup...")
bot.infinity_polling()
