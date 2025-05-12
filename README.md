# 🚀 CoinfestAsiaBlastBot

Bot Telegram otomatis untuk me-*blast* konten dari 1 channel tertentu ke banyak grup, tanpa label *forwarded*, dan dengan kemampuan mention member tertentu berdasarkan data dari Google Sheets. Dibuat khusus untuk kebutuhan manajemen komunitas Coinfest Asia Partner.

---

## ✨ Fitur Utama

- 🔗 **Forward otomatis tanpa label "forwarded"** dari satu channel resmi ke banyak grup.
- 📣 **Mention user berbeda di tiap grup** sesuai dengan kolom `Mentions` pada Google Sheet.
- 🆕 **Otomatis menyimpan ID & nama grup baru** ke Google Sheets saat bot ditambahkan.
- ✅ **Validasi channel sumber blast** hanya dari `SOURCE_CHANNEL_ID` agar tidak disalahgunakan.
- 🌐 **Berbasis cloud (Railway)** dan tanpa perlu server lokal.

---

## 🧠 Alur Kerja

1. Bot ditambahkan ke sebuah grup → grup otomatis dicatat di Google Sheet.
2. Admin channel mengirim pesan ke channel resmi.
3. Bot akan:
   - Kirim ulang konten (text, foto, video, dokumen) ke semua grup yang tercatat.
   - Tambahkan mention (jika tersedia) di bawah pesan utama.

---

## 📁 Struktur Sheet Google

| Group ID     | Group Name     | Mentions             | Timestamp             |
|--------------|----------------|-----------------------|------------------------|
| -1234567890  | Grup A         | @user1 @user2         | 2025-05-12 11:00:00    |
| -9876543210  | Grup B         | @partner1             | 2025-05-12 11:05:00    |

> Kolom `Mentions` akan otomatis ditambahkan saat bot dimasukkan ke grup. Kamu bisa edit sendiri kolom mention-nya.

---

## ⚙️ Setup di Railway

### 1. Upload kode ke GitHub, lalu connect repo-mu ke Railway.

### 2. Masukkan Environment Variables:

| Key                | Value                                                  |
|--------------------|--------------------------------------------------------|
| `BOT_TOKEN`        | Token dari BotFather                                   |
| `SHEET_ID`         | ID dari Google Sheet (contoh: `1Xxxx...`)              |
| `GOOGLE_CREDS_RAW` | Salin seluruh isi file `.json` dari Google Service Acc |
| `SOURCE_CHANNEL_ID`| ID channel sumber blast (contoh: `-1002634078790`)     |

---

## 💬 Format Pesan yang Didukung

- ✅ Text
- ✅ Photo (dengan caption)
- ✅ Video (dengan caption)
- ✅ Document (dengan caption)
- ✅ Link, bold, italic, dan format lainnya akan tetap tampil selama dikirim dari channel.

---

## 🛡️ Keamanan

- Bot hanya akan menanggapi pesan dari channel yang ID-nya cocok dengan `SOURCE_CHANNEL_ID`.
- Tidak ada command publik yang bisa disalahgunakan.

---

## 🧪 Tips Testing

1. Kirim pesan ke channel yang sudah diatur.
2. Tambahkan bot ke grup baru → Google Sheet akan otomatis bertambah.
3. Edit kolom `Mentions` untuk mengatur siapa saja yang akan di-mention per grup.

---

## 🧹 Maintenance & Customization

- Hapus grup dari sheet untuk menghentikan blast ke grup tersebut.
- Ubah mention langsung dari Google Sheet.
- Pastikan format sheet selalu 4 kolom: `Group ID`, `Group Name`, `Mentions`, `Timestamp`.

---

## 🙌 Credits

Dibuat dan dikustomisasi untuk **Coinfest Asia Partner Operations** oleh tim Coinvestasi 🚀
