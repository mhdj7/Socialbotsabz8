# وارد کردن کتابخانه‌های مورد نیاز
import os
import asyncio
import logging
from flask import Flask, request, Response
import telegram
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
import google.generativeai as genai

# تنظیمات اولیه لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن‌ها از متغیرهای محیطی
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تعریف مراحل مکالمه
SELECTING_ACTION, ASKING_TOPIC = range(2)

# --- توابع اصلی بات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع مکالمه و نمایش کیبورد اصلی."""
    user = update.effective_user
    keyboard = [
        [KeyboardButton("📝 ساخت سناریو جدید")],
        # می‌توانید دکمه‌های دیگری هم در آینده اینجا اضافه کنید
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_html(
        f"سلام {user.mention_html()}! 👋\n\n"
        "من دستیار هوشمند سوشال مدیای شما هستم. لطفاً از دکمه‌های زیر استفاده کنید.",
        reply_markup=reply_markup,
    )
    return SELECTING_ACTION

async def request_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """پس از کلیک روی دکمه، از کاربر موضوع را میپرسد."""
    await update.message.reply_text(
        "عالیه! لطفاً موضوعی که برای آن سناریو می‌خواهی را به صورت یک متن کامل برایم بنویس."
    )
    return ASKING_TOPIC

async def generate_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """موضوع را از کاربر دریافت کرده، سناریو تولید میکند و مکالمه را به نقطه شروع برمیگرداند."""
    try:
        topic = update.message.text
        if not topic:
            await update.message.reply_text("موضوعی دریافت نشد. لطفاً دوباره تلاش کن.")
            return ASKING_TOPIC

        await update.message.chat.send_action(action="typing")

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        شما یک متخصص تولید محتوا و سناریونویس حرفه‌ای برای اینستاگرام هستید.
        برای موضوع زیر، یک سناریوی کامل برای یک ویدیوی ریلز بنویس.
        موضوع: "{topic}"
        خروجی شامل این بخش‌ها باشد: قلاب، بدنه سناریو، کپشن پیشنهادی، فراخوان به اقدام و هشتگ‌ها.
        """
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)

    except Exception as e:
        logger.error(f"An error occurred in generate_scenario: {e}")
        await update.message.reply_text("متاسفانه مشکلی در پردازش درخواست شما پیش آمد.")

    # بعد از اتمام کار، کاربر را به منوی اصلی برمیگردانیم
    return await start(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مکالمه را لغو کرده و به نقطه شروع برمیگرداند."""
    await update.message.reply_text("عملیات لغو شد.")
    return await start(update, context)

# --- تنظیمات وب‌سرور و بات ---
# ساخت اپلیکیشن بات
application = Application.builder().token(TELEGRAM_TOKEN).build()

# ساخت ConversationHandler برای مدیریت مکالمه
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECTING_ACTION: [
            MessageHandler(
                filters.Regex("^📝 ساخت سناریو جدید$"), request_topic
            )
        ],
        ASKING_TOPIC: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, generate_scenario)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
)

application.add_handler(conv_handler)

# فعال‌سازی اولیه بات
asyncio.run(application.initialize())

# ساخت وب‌سرور Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello! Bot is running."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return Response("ok", status=200)
