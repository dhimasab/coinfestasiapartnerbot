# 🚀 Coinfest Asia Partner Blast Bot

Bot ini digunakan untuk **memforward konten dari Telegram Channel** ke banyak grup secara otomatis, sekaligus mengirim **mention khusus** ke setiap grup. Semua data grup dan mention dikelola lewat **Google Sheets**.

---

## ✨ Fitur Utama

- ✅ Forward konten dari channel ke grup secara otomatis
- ✅ Support semua jenis konten: text, foto, video, dokumen
- ✅ Mention otomatis berdasarkan data di Google Sheet
- ✅ Tidak menampilkan label “Forwarded from...”
- ✅ Menyimpan grup baru ke Sheet saat bot ditambahkan
- ✅ Format hyperlink & bold dari caption tetap terjaga

---

## 🛠️ Setup di Railway

1. **Fork / clone** repo ini ke akun GitHub kamu
2. Deploy ke Railway:
   - Connect GitHub → pilih repo ini
   - Tambahkan variabel-variabel berikut di tab **Variables**:
     - `BOT_TOKEN` → token dari [@BotFather](https://t.me/botfather)
     - `SHEET_ID` → ID dari Google Sheet kamu
     - `GOOGLE_CREDS_RAW` → isi file JSON dari service account Google kamu
3. Set command:  
