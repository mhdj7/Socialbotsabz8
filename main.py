# main.py
import os
import asyncio
import logging
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application

# وارد کردن handler سناریو از فایل دیگر
from handlers.scenario_handler import scenario_conv_handler

# تنظیمات اولیه لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن تلگرام
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# --- تنظیمات وب‌سرور و بات ---
# ساخت اپلیکیشن بات
application = Application.builder().token(TELEGRAM_TOKEN).build()

# اضافه کردن Conversation Handler سناریو به اپلیکیشن
application.add_handler(scenario_conv_handler)

# فعال‌سازی اولیه بات
asyncio.run(application.initialize())

# ساخت وب‌سرور Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello! Modular Bot is running."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return Response("ok", status=200)
