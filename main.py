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
GOOGLE_CREDS_RAW = os.getenv("GOOGLE_CREDS_RAW")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan di environment variables!")
if not SHEET_ID:
    raise ValueError("SHEET_ID tidak ditemukan di environment variables!")
if not GOOGLE_CREDS_RAW:
    raise ValueError("GOOGLE_CREDS_RAW tidak ditemukan di environment variables!")

# Setup Google Sheets access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_path = "/tmp/google-creds.json"

with open(creds_path, "w") as f:
    f.write(GOOGLE_CREDS_RAW)

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# Inisialisasi bot
bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Handler untuk menerima postingan dari channel dan forward ke semua grup di Google Sheet
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'sticker'])
def forward_post_to_groups(message):
    try:
        group_ids = sheet.col_values(1)[1:]  # Skip header
    except Exception as e:
        print(f"❌ Gagal mengambil data dari Google Sheet: {e}")
        return

    for group_id in group_ids:
        try:
            group_id_int = int(group_id)
            bot.forward_message(chat_id=group_id_int, from_chat_id=message.chat.id, message_id=message.message_id)
            print(f"✅ Berhasil forward ke group {group_id}")
        except Exception as e:
            print(f"❌ Gagal kirim ke {group_id}: {e}")

# ✅ Handler saat bot ditambahkan ke grup baru
@bot.my_chat_member_handler()
def auto_add_group(event):
    if event.new_chat_member.status in ['member', 'administrator']:
        chat_id = str(event.chat.id)
        chat_name = event.chat.title or "Unnamed Group"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            existing_ids = sheet.col_values(1)
        except Exception as e:
            print(f"❌ Gagal membaca sheet: {e}")
            existing_ids = []

        if chat_id not in existing_ids:
            try:
                sheet.append_row([chat_id, chat_name, timestamp])
                print(f"🆕 Grup baru ditambahkan: {chat_name} (ID: {chat_id})")
            except Exception as e:
                print(f"❌ Gagal menulis ke Google Sheet: {e}")
        else:
            print(f"ℹ️ Grup sudah ada: {chat_name} (ID: {chat_id})")

# Start polling
print("🤖 Bot aktif... Menunggu pesan dari channel atau event grup...")
bot.infinity_polling()
