import os
import json
import gspread
import telebot
from datetime import datetime
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDS_RAW = os.getenv("GOOGLE_CREDS_RAW")
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID", "0"))  # ID channel yang diizinkan

# Validasi env
if not all([BOT_TOKEN, SHEET_ID, GOOGLE_CREDS_RAW, SOURCE_CHANNEL_ID]):
    raise ValueError("Missing one or more required environment variables.")

# Simpan kredensial Google ke file sementara
creds_path = "/tmp/google-creds.json"
with open(creds_path, "w") as f:
    f.write(GOOGLE_CREDS_RAW)

# Setup akses Google Sheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# Inisiasi bot
bot = telebot.TeleBot(BOT_TOKEN)

# Ambil data grup dari sheet (hanya yang statusnya "Aktif")
def get_target_groups():
    records = sheet.get_all_records()
    return [
        {
            "id": int(row["Group ID"]),
            "mention": row.get("Mentions", "").strip()
        }
        for row in records
        if row.get("Group ID") and row.get("Status", "").strip().lower() == "aktif"
    ]

# Kirim ulang pesan dari channel (jika channel-nya terdaftar)
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document'])
def repost_message(message):
    if message.chat.id != SOURCE_CHANNEL_ID:
        print(f"🚫 Channel tidak diizinkan: {message.chat.id}")
        return

    groups = get_target_groups()
    for group in groups:
        group_id = group["id"]
        mention = group["mention"]
        try:
            if message.content_type == 'text':
                bot.send_message(group_id, message.text, entities=message.entities)
            elif message.content_type == 'photo':
                bot.send_photo(group_id, message.photo[-1].file_id, caption=message.caption, caption_entities=message.caption_entities)
            elif message.content_type == 'video':
                bot.send_video(group_id, message.video.file_id, caption=message.caption, caption_entities=message.caption_entities)
            elif message.content_type == 'document':
                bot.send_document(group_id, message.document.file_id, caption=message.caption, caption_entities=message.caption_entities)

            print(f"✅ Berhasil kirim ke {group_id} ({message.content_type})")

            if mention:
                bot.send_message(group_id, mention)
                print(f"💬 Mention terkirim ke {group_id}: {mention}")
        except Exception as e:
            print(f"❌ Gagal kirim ke {group_id}: {e}")

# Tambahkan grup ke Google Sheet saat bot dimasukkan
@bot.my_chat_member_handler()
def auto_add_group(event):
    if event.new_chat_member.status in ['member', 'administrator']:
        chat_id = event.chat.id
        chat_name = event.chat.title or "Unnamed Group"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing = sheet.get_all_records()
        existing_ids = [str(row["Group ID"]) for row in existing]

        if str(chat_id) not in existing_ids:
            sheet.append_row([str(chat_id), chat_name, "", timestamp, "Aktif"])
            print(f"🆕 Grup baru ditambahkan: {chat_name} (ID: {chat_id})")
        else:
            print(f"ℹ️ Grup sudah terdaftar: {chat_name} (ID: {chat_id})")

# Cari message id
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document'])
def debug_forward_info(message):
    if message.forward_from_chat:
        print("Forwarded from:", message.forward_from_chat.id)
        print("Message ID:", message.forward_from_message_id)

# Start polling
print("🤖 Bot aktif... Menunggu pesan dari channel yang diizinkan...")
bot.infinity_polling()
