# handlers/scenario_handler.py
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
import google.generativeai as genai
import os

# وارد کردن توابع و متغیرهای مربوط به ترند از فایل دیگر
from .trends_handler import ask_trend_category, send_videos_by_category, ASKING_TREND_CATEGORY

# تنظیمات لاگ
logger = logging.getLogger(__name__)

# تعریف تمام مراحل مکالمه‌های مختلف
(SELECTING_ACTION, BRAND, TONE, TOPIC, GOAL, STYLE, PLATFORM) = range(7)

# --- توابع مکالمه ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع بات و نمایش منوی اصلی."""
    keyboard = [["📝 سناریو نویسی"], ["🗓️ ساخت کلندر", "🔥 چی ترنده؟"]]
    await update.message.reply_text(
        "سلام! به دستیار هوشمند سوشال مدیای خود خوش آمدید. لطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return SELECTING_ACTION

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """کاربر را به منوی اصلی برمیگرداند و مکالمه فعلی را پایان میدهد."""
    await start(update, context)
    return ConversationHandler.END

async def ask_brand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "عالیه! وارد بخش سناریونویسی شدیم.\n\n"
        "ابتدا، لطفاً برند و محصول خود را به طور خلاصه معرفی کنید.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return BRAND

# ... (تمام توابع receive_ از اینجا تا generate_final_scenario بدون تغییر هستند) ...
async def receive_brand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['brand'] = update.message.text
    keyboard = [["رسمی"], ["متوسط (نه رسمی، نه صمیمی)"], ["صمیمی"]]
    await update.message.reply_text("مرحله ۲: لحن مورد نظر برند شما چیست؟", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return TONE
async def receive_tone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tone'] = update.message.text
    await update.message.reply_text("مرحله ۳: موضوع اصلی این سناریو چیست؟", reply_markup=ReplyKeyboardRemove())
    return TOPIC
async def receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['topic'] = update.message.text
    keyboard = [["افزایش آگاهی از برند", "فروش"], ["تعامل", "جذب لید"]]
    await update.message.reply_text("مرحله ۴: هدف اصلی شما چیست؟", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return GOAL
async def receive_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['goal'] = update.message.text
    keyboard = [["داستان‌سرایی (Storytelling)"], ["قلاب > داستان > پیشنهاد"], ["مشکل > راه‌حل (PAS)"], ["فرمول AIDA"]]
    await update.message.reply_text("مرحله ۵: کدام سبک سناریو را ترجیح می‌دهید؟", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return STYLE
async def receive_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['style'] = update.message.text
    keyboard = [["ریلز", "پست اسلایدی"], ["پست تک عکس", "اینفوگرافی"], ["ویدیو بلند یوتیوبی"]]
    await update.message.reply_text("مرحله ۶ (آخر): این محتوا در چه قالبی منتشر خواهد شد؟", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return PLATFORM

async def generate_final_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['platform'] = update.message.text
    await update.message.reply_text("عالی! تمام اطلاعات دریافت شد. لطفاً چند لحظه صبر کنید...", reply_markup=ReplyKeyboardRemove())
    try:
        user_choices = context.user_data
        prompt = f"""
        شما یک سناریونویس حرفه‌ای و خلاق در حوزه شبکه‌های اجتماعی هستید. با توجه به اطلاعات زیر، یک سناریوی کامل و جذاب بنویس:

        - برند و محصول: {user_choices.get('brand')}
        - موضوع محتوا: {user_choices.get('topic')}
        - لحن برند: {user_choices.get('tone')}
        - هدف از محتوا: {user_choices.get('goal')}
        - سبک سناریو: {user_choices.get('style')}
        - قالب انتشار: {user_choices.get('platform')}

        لطفاً خروجی شامل این بخش‌ها باشد:
        1.  **عنوان/قلاب جذاب (Hook):** چند ایده برای شروع طوفانی.
        2.  **بدنه سناریو:** توضیحات گام به گام بصری و متنی.
        3.  **کپشن پیشنهادی:** یک کپشن کامل و بهینه شده.
        4.  **فراخوان به اقدام (CTA):** یک جمله واضح برای تشویق کاربر.
        5.  **هشتگ‌ها:** مجموعه‌ای از هشتگ‌های مرتبط.
        6. حتما به سبک سناریو درخواست شده دقت کن و مثل یک متخصص ماهر نویسندگی که به جدید ترین و خلاقانه ترین مهارت های سناریو نویسی مسلط هست سناریو رو تولید کن.
        از ایموجی ها برای زیبا تر و مرتب تر شدن متن استفاده کن
        در نهایت هم بنویس "ارائه شده توسط تیم سوشال مدیا سبز"
        """
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error in final scenario generation: {e}")
        await update.message.reply_text("متاسفانه در تولید سناریو خطایی رخ داد.")

    await start(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("عملیات لغو شد.", reply_markup=ReplyKeyboardRemove())
    await start(update, context)
    return ConversationHandler.END

# تعریف ConversationHandler اصلی
main_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECTING_ACTION: [
            MessageHandler(filters.Regex("^📝 سناریو نویسی$"), ask_brand),
            MessageHandler(filters.Regex("^🔥 چی ترنده؟$"), ask_trend_category),
        ],
        BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_brand)],
        TONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tone)],
        TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_goal)],
        STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_style)],
        PLATFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_final_scenario)],
        ASKING_TREND_CATEGORY: [
            MessageHandler(filters.Regex("^(ویدیو های دیالوگی|ویدیو های مینیمال بدون چهره|ایده های فان)$"), send_videos_by_category),
            MessageHandler(filters.Regex("^بازگشت به منوی اصلی 🔙$"), back_to_main_menu), # <-- رفع باگ: فاصله اضافی حذف شد
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False 
)
