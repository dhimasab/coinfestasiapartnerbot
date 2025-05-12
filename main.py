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

# Init bot
bot = telebot.TeleBot(BOT_TOKEN)

# Fungsi cek apakah chat_id sudah ada di sheet
def is_group_recorded(chat_id):
    try:
        ids = sheet.col_values(1)
        return str(chat_id) in ids
    except:
        return False

# Fungsi menambahkan grup ke sheet
def add_group_to_sheet(chat_id, chat_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([str(chat_id), chat_name, timestamp])
    print(f"📝 Grup ditambahkan ke Google Sheet: {chat_name} ({chat_id})")

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

            # Cek dan simpan ke Google Sheet jika belum ada
            try:
                chat_info = bot.get_chat(group_id)
                chat_title = chat_info.title or 'Unknown Group'
                if not is_group_recorded(group_id):
                    add_group_to_sheet(group_id, chat_title)
            except Exception as e:
                print(f"❗ Gagal ambil info grup: {e}")

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
            group_ids.append(chat_id)
            with open('groups.json', 'w') as f:
                json.dump(group_ids, f)
            print(f"🆕 Grup baru ditambahkan: {chat_name} (ID: {chat_id})")

            if not is_group_recorded(chat_id):
                add_group_to_sheet(chat_id, chat_name)
        else:
            print(f"ℹ️ Grup sudah ada: {chat_name} (ID: {chat_id})")

# Start polling
print("🤖 Bot aktif... Menunggu pesan dari channel atau event grup...")
bot.infinity_polling()
