import telebot
import json
import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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

def get_groups_from_sheet():
    records = sheet.get_all_records()
    return [
        {
            "id": int(row["Group ID"]),
            "mention": row.get("Mentions", "").strip()
        }
        for row in records if row.get("Group ID")
    ]

@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document', 'sticker'])
def repost_to_groups(message):
    groups = get_groups_from_sheet()
    for group in groups:
        group_id = group["id"]
        mention_text = group["mention"]
        try:
            if message.text:
                bot.send_message(group_id, message.text)
            elif message.photo:
                file_id = message.photo[-1].file_id
                caption = message.caption or ""
                bot.send_photo(group_id, file_id, caption=caption)
            elif message.video:
                caption = message.caption or ""
                bot.send_video(group_id, message.video.file_id, caption=caption)
            elif message.document:
                caption = message.caption or ""
                bot.send_document(group_id, message.document.file_id, caption=caption)
            elif message.sticker:
                bot.send_sticker(group_id, message.sticker.file_id)

            print(f"✅ Konten berhasil dikirim ke {group_id}")

            if mention_text:
                bot.send_message(group_id, mention_text)
                print(f"💬 Mention terkirim ke group {group_id}: {mention_text}")
        except Exception as e:
            print(f"❌ Gagal kirim ke {group_id}: {e}")

@bot.my_chat_member_handler()
def auto_add_group(event):
    if event.new_chat_member.status in ['member', 'administrator']:
        chat_id = event.chat.id
        chat_name = event.chat.title or 'Unnamed Group'
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing_ids = [row["Group ID"] for row in sheet.get_all_records()]
        if str(chat_id) not in existing_ids:
            sheet.append_row([str(chat_id), chat_name, "", timestamp])
            print(f"🆕 Grup baru ditambahkan: {chat_name} (ID: {chat_id})")
        else:
            print(f"ℹ️ Grup sudah ada: {chat_name} (ID: {chat_id})")

print("🤖 Bot aktif... Menunggu pesan dari channel atau event grup...")
bot.infinity_polling()
