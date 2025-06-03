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
        updated = False

        for idx, row in enumerate(existing, start=2):  # start=2 karena header di baris 1
            if row.get("Group Name", "").strip() == chat_name.strip():
                sheet.update_cell(idx, 1, str(chat_id))  # Update Group ID (kolom A)
                sheet.update_cell(idx, 4, timestamp)     # Update timestamp (kolom D)
                print(f"🔁 Group ID diperbarui: {chat_name} (ID baru: {chat_id})")
                log_event("Update Group ID", group_id=chat_id, group_name=chat_name, detail="Group ID updated due to name match")
                updated = True
                break

        if not updated:
            sheet.append_row([str(chat_id), chat_name, "", timestamp, "Aktif"])
            print(f"🆕 Grup baru ditambahkan: {chat_name} (ID: {chat_id})")
            log_event("New Group Added", group_id=chat_id, group_name=chat_name, detail="Group ID baru ditambahkan")

        # ✅ Pesan baru yang ditambahkan ke dalam grup
        bot.send_message(chat_id, "Hi, please send this group's invitation link so we can invite the rest of our team.")

# Handler untuk menyimpan invite link ke Sheet1 kolom F
@bot.message_handler(func=lambda msg: msg.text and ("t.me/joinchat/" in msg.text or "t.me/+" in msg.text or "t.me/" in msg.text))
def handle_invite_link(msg):
    try:
        invite_link = msg.text.strip()
        group_id = str(msg.chat.id)

        bot_sheet = client.open_by_key(SHEET_ID).worksheet("Sheet1")
        all_data = bot_sheet.get_all_records()

        found = False
        for idx, row in enumerate(all_data, start=2):  # start=2 karena header di baris 1
            if str(row.get("Group ID")).strip() == group_id:
                bot_sheet.update_cell(idx, 6, invite_link)  # Kolom F = kolom ke-6 (Invite Link)
                print(f"✅ Invite link saved to Sheet1 row {idx}")
                bot.reply_to(msg, f"✅ Thank you! Your invite link has been saved.")
                found = True
                break

        if not found:
            bot.reply_to(msg, "⚠️ Group ID not found in sheet. Please ensure this group is registered.")
            print(f"❌ Group ID {group_id} not found in Sheet1.")

    except Exception as e:
        print(f"❌ Failed to save invite link: {e}")
        bot.reply_to(msg, "⚠️ Failed to save the invite link. Please try again later.")

# Kirim welcoming message dari message id yang ditentukan
@bot.message_handler(commands=['welcome'])
def send_welcome_message(message):
    try:
        group_id = message.chat.id
        print(f"🚀 Mengirim pesan welcome ke grup {group_id}")

        # Forward pesan dari channel ke grup
        bot.forward_message(
            chat_id=group_id,
            from_chat_id=int(os.getenv("WELCOME_CHAT_ID")),
            message_id=int(os.getenv("WELCOME_MESSAGE_ID"))
        )

        # Ambil mention dari Google Sheet
        records = sheet.get_all_records()
        for row in records:
            if str(row["Group ID"]) == str(group_id):
                mention = row.get("Mentions", "").strip()
                if mention:
                    bot.send_message(group_id, mention)
                    print(f"✅ Mention dikirim ke {group_id}: {mention}")
                break

    except Exception as e:
        print(f"❌ Gagal mengirim pesan welcome: {e}")

# Logging ke Sheet Logs
def log_event(event_type, group_id=None, group_name=None, detail=""):
    try:
        log_sheet = client.open_by_key(SHEET_ID).worksheet("Logs")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_sheet.append_row([timestamp, event_type, group_id or "", group_name or "", detail])
        print(f"📝 Logged: {event_type} | {group_id} | {detail}")
    except Exception as e:
        print(f"❌ Gagal logging: {e}")

# Start polling
print("🤖 Bot aktif... Menunggu pesan dari channel yang diizinkan...")
bot.infinity_polling()
