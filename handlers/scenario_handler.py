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

# تنظیمات لاگ
logger = logging.getLogger(__name__)

# تعریف مراحل مختلف مکالمه
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

async def ask_brand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مرحله ۱: پرسیدن نام برند/محصول."""
    context.user_data.clear() # پاک کردن اطلاعات مکالمه قبلی
    await update.message.reply_text(
        "عالیه! وارد بخش سناریونویسی شدیم.\n\n"
        "ابتدا، لطفاً برند و محصول خود را به طور خلاصه معرفی کنید. (مثال: کافه روبرو، ارائه دهنده قهوه تخصصی)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return BRAND

async def receive_brand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت برند و پرسیدن لحن."""
    context.user_data['brand'] = update.message.text
    keyboard = [["رسمی"], ["متوسط (نه رسمی، نه صمیمی)"], ["صمیمی"]]
    await update.message.reply_text(
        "مرحله ۲: لحن مورد نظر برند شما برای این محتوا چیست؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return TONE

async def receive_tone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت لحن و پرسیدن موضوع."""
    context.user_data['tone'] = update.message.text
    await update.message.reply_text(
        "مرحله ۳: موضوع اصلی این سناریو چیست؟ (مثال: معرفی قهوه جدید کلمبیا)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TOPIC

async def receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت موضوع و پرسیدن هدف."""
    context.user_data['topic'] = update.message.text
    keyboard = [["افزایش آگاهی از برند", "فروش"], ["تعامل", "جذب لید"]]
    await update.message.reply_text(
        "مرحله ۴: هدف اصلی شما از ساخت این محتوا چیست؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return GOAL

async def receive_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت هدف و پرسیدن سبک."""
    context.user_data['goal'] = update.message.text
    keyboard = [["داستان‌سرایی (Storytelling)"], ["قلاب > داستان > پیشنهاد"], ["مشکل > راه‌حل (PAS)"], ["فرمول AIDA"]]
    await update.message.reply_text(
        "مرحله ۵: کدام سبک سناریو را ترجیح می‌دهید؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return STYLE

async def receive_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت سبک و پرسیدن مدل انتشار."""
    context.user_data['style'] = update.message.text
    keyboard = [["ریلز", "پست اسلایدی"], ["پست تک عکس", "اینفوگرافی"], ["ویدیو بلند یوتیوبی"]]
    await update.message.reply_text(
        "مرحله ۶ (آخر): این محتوا در چه قالبی منتشر خواهد شد؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return PLATFORM

async def generate_final_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """جمع‌آوری تمام اطلاعات، ساخت پرامپت و ارسال به Gemini."""
    context.user_data['platform'] = update.message.text
    await update.message.reply_text("عالی! تمام اطلاعات دریافت شد. لطفاً چند لحظه صبر کنید تا سناریوی اختصاصی شما آماده شود...", reply_markup=ReplyKeyboardRemove())

    try:
        # ساخت پرامپت نهایی و دقیق
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
        """

        # ارسال به Gemini
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)

    except Exception as e:
        logger.error(f"Error in final scenario generation: {e}")
        await update.message.reply_text("متاسفانه در تولید سناریو خطایی رخ داد. لطفاً دوباره تلاش کنید.")

    # پایان مکالمه و بازگشت به منوی اصلی
    await start(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو مکالمه و بازگشت به منوی اصلی."""
    await update.message.reply_text("عملیات لغو شد.", reply_markup=ReplyKeyboardRemove())
    await start(update, context)
    return ConversationHandler.END

# تعریف ConversationHandler
scenario_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SELECTING_ACTION: [
            MessageHandler(filters.Regex("^📝 سناریو نویسی$"), ask_brand),
            # اینجا می‌توانید برای دکمه‌های دیگر هم ورودی تعریف کنید
        ],
        BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_brand)],
        TONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tone)],
        TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_goal)],
        STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_style)],
        PLATFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_final_scenario)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
