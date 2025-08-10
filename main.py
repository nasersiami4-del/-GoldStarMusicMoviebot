import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ==============================
# تنظیمات ربات
# ==============================
BOT_TOKEN = "8360522775:AAEUbSR_S7_mM7RPPMfkv6yk6WBXPiSy2sY"
PUBLIC_CHANNEL_ID = -1001081524118
PRIVATE_CHANNEL_ID = -1001311582958
ADMIN_IDS = [135019937]  # فقط ادمین اصلی
DATA_FILE = "seasons.json"

# ==============================
# مدیریت ذخیره و خواندن داده‌ها
# ==============================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(seasons, f, ensure_ascii=False, indent=2)

seasons = load_data()
active_season = None

# ==============================
# دستورات مخصوص ادمین
# ==============================
async def add_season(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_season
    if update.effective_user.id not in ADMIN_IDS:
        return

    if len(context.args) != 1:
        await update.message.reply_text("دستور درست: /add s1")
        return

    season_code = context.args[0]
    seasons[season_code] = []
    active_season = season_code
    save_data()
    await update.message.reply_text(f"📂 شروع اضافه کردن فایل‌ها برای فصل {season_code}\nبعد از اتمام بزن /done")

async def done_season(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_season
    if update.effective_user.id not in ADMIN_IDS:
        return
    await update.message.reply_text(f"✅ فصل {active_season} کامل شد.")
    active_season = None

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_season
    if update.effective_user.id not in ADMIN_IDS or not active_season:
        return

    file_id = None
    if update.message.video:
        file_id = update.message.video.file_id
    elif update.message.document:
        file_id = update.message.document.file_id
    elif update.message.audio:
        file_id = update.message.audio.file_id

    if file_id:
        seasons[active_season].append(file_id)
        save_data()
        await update.message.reply_text(f"📥 فایل ذخیره شد ({len(seasons[active_season])} عدد)")

async def post_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    season_codes = context.args
    if not season_codes:
        await update.message.reply_text("دستور: /post s1 s2 ...")
        return

    buttons = []
    for sc in season_codes:
        if sc in seasons:
            buttons.append([InlineKeyboardButton(f"{sc} 📥 دانلود", callback_data=f"dl:{sc}")])

    keyboard = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(
        chat_id=PUBLIC_CHANNEL_ID,
        text="🎬 سریال جدید آماده دانلود است:",
        reply_markup=keyboard
    )
    await update.message.reply_text("✅ پست به کانال عمومی ارسال شد.")

# ==============================
# دریافت درخواست دانلود
# ==============================
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("dl:"):
        season_code = data.split(":")[1]
        if season_code in seasons:
            await context.bot.send_message(chat_id=query.from_user.id, text=f"📤 ارسال فایل‌های {season_code} شروع شد...")
            for fid in seasons[season_code]:
                await context.bot.send_document(chat_id=query.from_user.id, document=fid)
        else:
            await query.message.reply_text("❌ این فصل موجود نیست.")

# ==============================
# اجرای ربات
# ==============================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("add", add_season))
    app.add_handler(CommandHandler("done", done_season))
    app.add_handler(CommandHandler("post", post_to_channel))
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), receive_file))
    app.add_handler(CallbackQueryHandler(button_click))

    print("🤖 ربات فعال شد...")
    app.run_polling()
