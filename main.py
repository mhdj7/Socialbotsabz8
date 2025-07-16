# main.py
import os
import logging
from telegram.ext import Application

# وارد کردن handler سناریو از فایل دیگر
from handlers.scenario_handler import scenario_conv_handler

# تنظیمات اولیه لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن و تنظیمات از متغیرهای محیطی
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
# پورت توسط Render به صورت خودکار فراهم می‌شود
PORT = int(os.environ.get("PORT", "8443"))
# آدرس سرویس شما در Render
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")


def main() -> None:
    """راه‌اندازی و اجرای بات."""
    # ساخت اپلیکیشن بات
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # اضافه کردن Conversation Handler سناریو به اپلیکیشن
    application.add_handler(scenario_conv_handler)

    # اجرای بات در حالت Webhook با استفاده از وب‌سرور داخلی
    # این تابع به صورت خودکار همه چیز را مدیریت می‌کند
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )

if __name__ == "__main__":
    main()
