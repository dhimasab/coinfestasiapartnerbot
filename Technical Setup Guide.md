# 🚀 CoinfestAsiaBlastBot – Technical Setup Guide

Telegram bot untuk me-blast pesan dari satu channel resmi ke banyak grup komunitas dengan fitur auto-mention, pengaturan dinamis lewat Google Sheet, dan berjalan 24/7 di Railway.

---

## 📦 Project Overview

- **Bahasa:** Python 3.10+
- **Library utama:** `pyTelegramBotAPI`, `gspread`, `dotenv`, `oauth2client`
- **Cloud hosting:** Railway
- **Database grup:** Google Sheet
- **Trigger utama:** Pesan yang dikirim ke channel tertentu

---

## 🧱 Folder Structure
project/
├── main.py
├── requirements.txt
├── .env (opsional untuk lokal


---

## 🧰 Step-by-Step Setup

### 1. 🔧 Setting Google Cloud Console (Service Account)

1. Masuk ke [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru atau pilih project aktif
3. Aktifkan **Google Sheets API** dan **Google Drive API**
4. Masuk ke menu **APIs & Services > Credentials**
5. Klik **Create Credentials → Service Account**
6. Setelah selesai, masuk ke Service Account > tab **KEYS**
7. Klik **Add Key → Create new key → JSON**
8. Simpan file `.json`, lalu:
   - Ubah jadi satu baris dengan `jq`:
     ```bash
     cat creds.json | jq -c
     ```
   - Salin hasilnya ke environment variable `GOOGLE_CREDS_RAW`

9. Share Google Sheet ke email service account kamu (misalnya: `blast-bot@your-project.iam.gserviceaccount.com`)  
   Beri akses sebagai **Editor**

---

### 2. 🗃️ Format Google Sheet

Buat sheet baru dengan kolom:
Group ID | Group Name | Mentions | Timestamp


- Group ID: ID grup Telegram
- Group Name: Nama grup (boleh dikosongkan, akan terisi otomatis)
- Mentions: Teks @mention custom (opsional)
- Timestamp: Diisi otomatis saat grup baru ditambahkan

---

### 3. 🧪 Setting Script Bot

**Isi `main.py`:**

- Mendeteksi pesan dari channel resmi
- Mengambil daftar grup dari Google Sheet
- Kirim konten (text, foto, video, dokumen) ke grup-grup tersebut
- Menyisipkan `@mention` tambahan jika tersedia
- Menyimpan grup baru ke Sheet saat bot ditambahkan ke grup

---

### 4. ☁️ Deploy ke Railway

#### ✅ Langkah-langkah:

1. Buat GitHub repo, push file `main.py` dan `requirements.txt`
2. Masuk ke [railway.app](https://railway.app)
3. Buat project baru > **Deploy from GitHub**
4. Railway akan mendeteksi project Python
5. Tambahkan **Environment Variables** berikut:

| Key                | Keterangan                                   |
|--------------------|----------------------------------------------|
| `BOT_TOKEN`         | Token bot dari [@BotFather](https://t.me/BotFather) |
| `SHEET_ID`          | ID dari Google Sheet kamu                   |
| `GOOGLE_CREDS_RAW`  | JSON Service Account versi 1 baris          |
| `SOURCE_CHANNEL_ID` | ID dari channel yang diizinkan (contoh: `-1002541764844`) |

> Railway akan otomatis install `requirements.txt` dan menjalankan bot dengan `infinity_polling`.

---

## ✅ Pesan yang Didukung

- Text
- Photo + caption
- Video + caption
- Document + caption
- Markdown formatting (bold, italic, link, dll)

---

## 🧪 Tes

1. Tambahkan bot ke channel resmi (sebagai admin)
2. Aktifkan **"Post as Bot"** di channel
3. Tambahkan bot ke grup → grup akan masuk otomatis ke Sheet
4. Kirim pesan ke channel → bot akan broadcast ke semua grup yang terdaftar

---

## 🛠 Maintenance Tips

- Hapus baris di Sheet untuk menghentikan broadcast ke grup
- Ganti `Mentions` langsung dari Google Sheet
- Format Sheet harus selalu 4 kolom: `Group ID`, `Group Name`, `Mentions`, `Timestamp`

---

## 🛡️ Keamanan

- Bot hanya memproses pesan dari channel yang ID-nya sesuai `SOURCE_CHANNEL_ID`
- Tidak ada command publik, tidak bisa dikendalikan oleh user

---

## 🙌 Credits

Dibuat oleh Dhimas untuk kebutuhan distribusi ke komunitas partner Coinfest Asia 2025 🚀
