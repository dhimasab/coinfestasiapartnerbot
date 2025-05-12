import telebot
import json
import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

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

google_creds_raw = os.getenv("GOOGLE_CREDS_RAW")
if not google_creds_raw:
    raise ValueError("GOOGLE_CREDS_RAW tidak ditemukan di environment variables!")

with open(creds_path, "w") as f:
    f.write(google_creds_raw)

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

bot = telebot.TeleBot(BOT_TOKEN)

# Fungsi untuk ambil grup & mention dari sheet
def get_groups_and_mentions():
    records = sheet.get_all_records()
    return [(str(row['group_id']), row['mention']) for row in records if row['group_id']]

# ✅ Handler untuk menerima postingan dari channel dan repost ke grup (tanpa label forwarded)
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'sticker'])
def repost_to_groups(message):
    group_data = get_groups_and_mentions()
    for group_id, mention in group_data:
        try:
            if message.content_type == 'text':
                text = message.text + f"\n\n{mention}" if mention else message.text
                bot.send_message(chat_id=group_id, text=text)

            elif message.content_type == 'photo':
                file_id = message.photo[-1].file_id
                caption = message.caption or ''
                caption += f"\n\n{mention}" if mention else ''
                bot.send_photo(chat_id=group_id, photo=file_id, caption=caption)

            elif message.content_type == 'video':
                file_id = message.video.file_id
                caption = message.caption or ''
                caption += f"\n\n{mention}" if mention else ''
                bot.send_video(chat_id=group_id, video=file_id, caption=caption)

            elif message.content_type == 'document':
                file_id = message.document.file_id
                caption = message.caption or ''
                caption += f"\n\n{mention}" if mention else ''
                bot.send_document(chat_id=group_id, document=file_id, caption=caption)

            elif message.content_type == 'sticker':
                bot.send_sticker(chat_id=group_id, sticker=message.sticker.file_id)

            print(f"✅ Dikirim ke {group_id}")
        except Exception as e:
            print(f"❌ Gagal kirim ke {group_id}: {e}")
        time.sleep(1)  # Hindari terlalu cepat

# ✅ Handler saat bot ditambahkan ke grup
@bot.my_chat_member_handler()
def auto_add_group(event):
    if event.new_chat_member.status in ['member', 'administrator']:
        chat_id = str(event.chat.id)
        chat_name = event.chat.title or 'Unnamed Group'
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing = sheet.get_all_records()
        known_ids = [str(row['group_id']) for row in existing]

        if chat_id not in known_ids:
            sheet.append_row([chat_id, chat_name, '', timestamp])
            print(f"🆕 Grup baru ditambahkan: {chat_name} (ID: {chat_id})")
        else:
            print(f"ℹ️ Grup sudah ada: {chat_name} (ID: {chat_id})")

print("🤖 Bot aktif dengan mode repost... Menunggu pesan dari channel...")
bot.infinity_polling()
