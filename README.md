# 🤖 Coinfest Asia Partner Blast Bot

Bot ini bertugas untuk:
- Meneruskan pesan dari channel Telegram ke berbagai grup partner secara otomatis
- Menyisipkan mention khusus ke tiap grup (bila ada), sesuai daftar di Google Sheet
- Menjaga format asli konten seperti **bold**, _italic_, dan hyperlink jika bukan *forwarded*

---

## 📦 Fitur Utama

✅ Forward otomatis dari 1 channel ke banyak grup  
✅ Penyisipan mention unik untuk tiap grup  
✅ Integrasi langsung ke Google Sheet untuk sinkronisasi dinamis  
✅ Otomatis menyimpan grup baru yang ditambahkan ke Google Sheet  
✅ Support **format konten lengkap**: teks, foto, video, dokumen, stiker  
✅ Bisa di-*deploy* secara gratis via [Railway](https://railway.app)  

---

## 📄 Format Google Sheet

Gunakan template seperti ini:

| Group ID     | Group Name                   | Mentions             | Timestamp           |
|--------------|------------------------------|-----------------------|---------------------|
| `-123456789` | Grup A                       | `@user1 @user2`      | 2025-05-12 05:00:00 |
| `-987654321` | Grup B                       |                       | 2025-05-12 05:01:00 |

**Keterangan Kolom:**
- 🆔 **Group ID** — ID grup Telegram, otomatis terisi saat bot ditambahkan ke grup
- 🧾 **Group Name** — Nama grup untuk dokumentasi internal
- 🧑‍🤝‍🧑 **Mentions** — Mention (username) yang akan dikirim setelah konten, bisa lebih dari 1
- ⏰ **Timestamp** — Waktu bot bergabung ke grup, otomatis diisi

---

## 🚀 Cara Kerja Bot

1. Bot dipasang ke channel sebagai **admin dengan akses baca**
2. Setiap pesan masuk dari channel, bot akan:
   - Menyalin konten (teks, media, caption) dan mengirim ke seluruh grup
   - Menambahkan teks mention di bawahnya (jika tersedia dari Sheet)
3. Setiap kali bot ditambahkan ke grup baru:
   - ID & nama grup langsung ditulis ke Google Sheet
   - Timestamp gabung juga tercatat otomatis
4. Seluruh data grup disinkronkan dari Sheet — **tidak perlu edit manual di `groups.json`**

---

## 📌 Catatan Teknis

- Bot tidak akan mengirim mention jika kolom `Mentions` kosong
- Konten akan tetap memiliki format teks asli (**bold**, _italic_, link) **hanya jika bukan pesan forwarded**
- Jika ingin _tidak_ terlihat sebagai “Forwarded from Channel”, gunakan metode repost yang menyalin konten satu per satu
- Jangan menjalankan lebih dari **1 instance bot secara bersamaan** — akan menyebabkan konflik polling

---

## 🛠️ Setup & Deployment

### 1. Siapkan Google Cloud & Sheet

- Buat Google Sheet baru dengan format seperti di atas
- Buat Service Account di Google Cloud dan aktifkan:
  - Google Sheets API
  - Google Drive API
- Unduh credential JSON dan **isi ke dalam Railway variable**

### 2. Struktur Environment Variable

| Nama Variable                 | Keterangan                        |
|------------------------------|-----------------------------------|
| `BOT_TOKEN`                  | Token bot Telegram                |
| `SHEET_ID`                   | ID Google Sheet (ambil dari URL) |
| `GOOGLE_CREDS_RAW`           | Full JSON credential, bentuk string |

Contoh isi `GOOGLE_CREDS_RAW` bisa disalin dari file credential dan disimpan dalam bentuk ENV string (gunakan `Raw Editor` di Railway).

---

### 3. Deploy ke Railway

- Push project kamu ke GitHub
- Buat project baru di Railway → Connect GitHub → pilih repo kamu
- Set start command: `python main.py`
- Tambahkan environment variables seperti di atas
- Done ✅ Bot akan otomatis jalan dan mencatat semua aktivitas ke Logs Railway

---

## 💡 Tips Operasional

- Untuk kirim ulang **bukan sebagai forwarded**, gunakan fungsi repost: salin isi pesan secara manual
- Untuk menghindari error `409 conflict polling`, pastikan hanya 1 deployment aktif
- Cek log secara berkala lewat Railway untuk pantau pengiriman

---

## 🧪 Contoh Output Bot

### Chat Channel:

> 🌊 Cek jadwal venue Coinfest Asia 2025!  
> t.me/coinfestasia  

### Yang muncul di Grup A:

🌊 Cek jadwal venue Coinfest Asia 2025!
t.me/coinfestasia
@user1 @user2


---

## 📬 Kontak & Lisensi

Dibuat oleh tim Dhimas, tim Coinfest Asia untuk komunikasi internal dan partner.  
Lisensi: DMS — silakan fork dan gunakan dengan bijak.

