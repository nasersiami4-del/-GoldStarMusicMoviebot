import os
from flask import Flask, request
import telebot

# گرفتن توکن از Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN در Environment Variables تنظیم نشده")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# پاسخ ساده برای تست
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, f"سلام {message.from_user.first_name} 👋\nربات فعاله ✅")

# مسیر دریافت آپدیت‌ها (Webhook)
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return "OK", 200

# تنظیم وبهوک به محض بالا اومدن سرور
@app.before_first_request
def set_webhook():
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        raise ValueError("❌ RENDER_EXTERNAL_HOSTNAME تنظیم نشده")
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{hostname}/{TOKEN}")
    print(f"✅ Webhook set to https://{hostname}/{TOKEN}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
