# وارد کردن کتابخانه‌های مورد نیاز
import os
import asyncio
import logging
from flask import Flask, request, Response
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import google.generativeai as genai

# تنظیمات اولیه
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن‌ها از متغیرهای محیطی
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

# تابع برای دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"سلام {user.mention_html()}! 👋\n\n"
        "من یک بات همیشه فعال هستم و آماده‌ام تا برایت سناریوهای خلاقانه بنویسم.\n"
        "/scenario موضوع مورد نظر"
    )

# تابع برای تولید سناریو
async def generate_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        topic = " ".join(context.args)
        if not topic:
            await update.message.reply_text("لطفاً بعد از دستور /scenario، موضوع را هم بنویس.")
            return

        await update.message.chat.send_action(action='typing')

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')

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

# ساخت اپلیکیشن بات
application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("scenario", generate_scenario))

# بخش وب‌سرور با Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello! I am the bot's web server."

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return Response('ok', status=200)

# تابع اصلی برای اجرا
def run():
    # تنظیم Webhook
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.bot.set_webhook(url=WEBHOOK_URL))
    logger.info(f"Webhook set to {WEBHOOK_URL}")

    # اجرای وب‌سرور
    # پورت توسط Render به صورت خودکار تنظیم می‌شود.
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    run()
