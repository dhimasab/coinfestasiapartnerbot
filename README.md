# 🚀 CoinfestAsiaBlastBot

A Telegram bot designed to *blast* content from a specific channel to multiple groups automatically—without the “forwarded” label—and with the ability to mention specific users per group based on data from Google Sheets. Built specifically for Coinfest Asia Partner community management needs.

---

## ✨ Key Features

- 🔗 **Auto-forward without the “forwarded” label** from one official channel to multiple groups.
- 📣 **Mention different users in each group** based on the `Mentions` column in Google Sheets.
- 🆕 **Automatically saves new group IDs & names** to Google Sheets when the bot is added.
- ✅ **Validates blast source channel** using `SOURCE_CHANNEL_ID` to prevent misuse.
- 🌐 **Cloud-based (Railway)**, no local server required.

---

## 🧠 Workflow

1. Bot is added to a group → group is automatically recorded in Google Sheet.
2. Channel admin sends a message in the official channel.
3. Bot will:
   - Repost the content (text, photo, video, document) to all listed groups.
   - Add mentions (if available) below the main message.

---

## 📁 Google Sheet Structure

| Group ID     | Group Name     | Mentions             | Timestamp             |
|--------------|----------------|----------------------|------------------------|
| -1234567890  | Group A         | @user1 @user2        | 2025-05-12 11:00:00    |
| -9876543210  | Group B         | @partner1            | 2025-05-12 11:05:00    |

> The `Mentions` column will be auto-filled when the bot joins a group. You can manually edit the mention entries as needed.

---

## ⚙️ Railway Setup

### 1. Upload your code to GitHub, then connect the repo to Railway.

### 2. Add the following Environment Variables:

| Key                | Value                                                    |
|--------------------|----------------------------------------------------------|
| `BOT_TOKEN`        | Token from BotFather                                     |
| `SHEET_ID`         | ID of your Google Sheet (e.g., `1Xxxx...`)               |
| `GOOGLE_CREDS_RAW` | Paste the entire contents of your Service Account `.json` file |
| `SOURCE_CHANNEL_ID`| ID of the source channel for blasting (e.g., `-1002634078790`) |

---

## 💬 Supported Message Formats

- ✅ Text  
- ✅ Photo (with caption)  
- ✅ Video (with caption)  
- ✅ Document (with caption)  
- ✅ Links, bold, italic, and other formats are preserved if sent from the channel.

---

## 🛡️ Security

- Bot only responds to messages from the channel with an ID that matches `SOURCE_CHANNEL_ID`.
- No public commands are available for misuse.

---

## 🧪 Testing Tips

1. Send a message to the configured channel.
2. Add the bot to a new group → the group will auto-register in Google Sheet.
3. Edit the `Mentions` column to control which users are mentioned in each group.

---

## 🧹 Maintenance & Customization

- Remove a group from the sheet to stop blasting to it.
- Edit mentions directly from Google Sheet.
- Make sure the sheet always has 4 columns: `Group ID`, `Group Name`, `Mentions`, `Timestamp`.

---

## 🙌 Credits

Created and customized by Dhimas for **Coinfest Asia Partnership** 🚀
