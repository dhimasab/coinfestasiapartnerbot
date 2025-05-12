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

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_path = "/tmp/google-creds.json"

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

# ✅ Forward dan Mention
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'sticker'])
def forward_post_to_groups(message):
    try:
        records = sheet.get_all_records()
    except Exception as e:
        print(f"❌ Gagal ambil data sheet: {e}")
        return

    for row in records:
        try:
            group_id = int(row['Group ID'])
            mention_text = row.get('Mentions', '')

            # Forward
            bot.forward_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.message_id)
            print(f"✅ Forwarded ke group {group_id}")

            # Kirim mention setelah forward
            if mention_text.strip():
                bot.send_message(chat_id=group_id, text=mention_text)
                print(f"💬 Mention terkirim ke group {group_id}: {mention_text}")
        except Exception as e:
            print(f"❌ Error kirim ke {row.get('Group Name')} ({row.get('Group ID')}): {e}")

# ✅ Auto-save grup ke Sheet saat bot ditambahkan
@bot.my_chat_member_handler()
def auto_add_group(event):
    if event.new_chat_member.status in ['member', 'administrator']:
        chat_id = event.chat.id
        chat_name = event.chat.title or 'Unnamed Group'
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            existing = sheet.get_all_values()
            existing_ids = [row[0] for row in existing[1:] if row]

            if str(chat_id) not in existing_ids:
                sheet.append_row([str(chat_id), chat_name, timestamp, ""])  # Kosongin kolom Mention dulu
                print(f"🆕 Grup baru ditambahkan: {chat_name} (ID: {chat_id})")
            else:
                print(f"ℹ️ Grup sudah terdaftar: {chat_name} (ID: {chat_id})")
        except Exception as e:
            print(f"❌ Gagal nambah grup ke sheet: {e}")

# Start polling
print("🤖 Bot aktif... Menunggu pesan dari channel atau event grup...")
bot.infinity_polling()
