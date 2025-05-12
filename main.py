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
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

def get_groups_data():
    records = sheet.get_all_records()
    group_data = []
    for row in records:
        group_id = str(row.get("Group ID", "")).strip()
        mentions = row.get("Mentions", "").strip()
        if group_id:
            group_data.append({
                "group_id": group_id,
                "mentions": mentions
            })
    return group_data

@bot.channel_post_handler(content_types=["text", "photo", "video", "document", "sticker"])
def repost_to_groups(message):
    groups = get_groups_data()

    for group in groups:
        group_id = group["group_id"]
        mentions = group["mentions"]

        try:
            if message.text:
                bot.send_message(group_id, message.text)
            elif message.caption and message.photo:
                file_id = message.photo[-1].file_id
                bot.send_photo(group_id, file_id, caption=message.caption)
            elif message.caption and message.video:
                file_id = message.video.file_id
                bot.send_video(group_id, file_id, caption=message.caption)
            elif message.caption and message.document:
                file_id = message.document.file_id
                bot.send_document(group_id, file_id, caption=message.caption)
            elif message.sticker:
                bot.send_sticker(group_id, message.sticker.file_id)
            else:
                print(f"⚠️ Tidak dikenali: {group_id}")
                continue

            print(f"✅ Repost ke group {group_id}")

            if mentions:
                bot.send_message(group_id, mentions)
                print(f"💬 Mention terkirim ke group {group_id}: {mentions}")

        except Exception as e:
            print(f"❌ Gagal kirim ke group {group_id}: {e}")

print("🤖 Bot aktif... Menunggu pesan dari channel...")
bot.infinity_polling()
