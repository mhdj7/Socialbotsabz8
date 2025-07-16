# main.py
import os
import logging
from telegram.ext import Application

# **نکته مهم:** مطمئن شوید که نام وارد شده در اینجا (main_conv_handler)
# دقیقاً با نام تعریف شده در فایل scenario_handler.py یکسان است.
from handlers.scenario_handler import main_conv_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(main_conv_handler)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )

if __name__ == "__main__":
    main()
