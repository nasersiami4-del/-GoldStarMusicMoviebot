import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ÑÝÊä ãÊÛíÑåÇ ÇÒ ãÍíØ (Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "135019937"))
PUBLIC_CHANNEL_ID = os.getenv("PUBLIC_CHANNEL_ID")
PRIVATE_CHANNEL_ID = os.getenv("PRIVATE_CHANNEL_ID")

# ÐÎíÑå ÝÇíáåÇ ÏÑ í˜ Ïí˜ÔäÑí ÓÇÏå
series_data = {}

# ÝÞØ ÇÏãíä
def is_admin(user_id):
    return user_id == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ÓáÇã! Çíä ÑÈÇÊ ãÎÕæÕ ÇÑÓÇá ÓÑíÇáåÇÓÊ ??")

async def add_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return await update.message.reply_text("ÔãÇ ÏÓÊÑÓí äÏÇÑíÏ ?")

    if len(context.args) < 2:
        return await update.message.reply_text("ÇÓÊÝÇÏå: /add äÇã_ÓÑíÇá áíä˜1,áíä˜2,...")

    name = context.args[0]
    links = " ".join(context.args[1:]).split(",")
    series_data[name] = links
    await update.message.reply_text(f"? ÓÑíÇá '{name}' ÈÇ {len(links)} ÞÓãÊ ÇÖÇÝå ÔÏ.")

async def list_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not series_data:
        return await update.message.reply_text("?? åí ÓÑíÇáí ËÈÊ äÔÏå.")

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"series_{name}")]
        for name in series_data
    ]
    await update.message.reply_text("?? áíÓÊ ÓÑíÇáåÇ:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("series_"):
        name = query.data.split("_", 1)[1]
        links = series_data.get(name, [])
        for link in links:
            await context.bot.send_message(chat_id=query.from_user.id, text=link)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_series))
    app.add_handler(CommandHandler("list", list_series))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

