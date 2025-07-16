# handlers/trends_handler.py
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

# تنظیمات لاگ
logger = logging.getLogger(__name__)

# =================================================================
# >> شناسه‌های ویدیوهای خود را در اینجا وارد کنید <<
# هر دسته می‌تواند شامل هر تعداد شناسه باشد
TREND_VIDEOS = {
    "ویدیو های دیالوگی": [
        "BAACAgQAAxkBAAEB2J9od_3-jAh95gHAK-a5oJTG9YWsDQACehsAApUowVNJqrNjQld6AjYE", 
      
    ],
    "ویدیو های مینیمال بدون چهره": [
        "BAACAgQAAxkBAAEB2J9od_3-jAh95gHAK-a5oJTG9YWsDQACehsAApUowVNJqrNjQld6AjYE",
      
    ],
    "ایده های فان": [
        "BAACAgQAAxkBAAEB2J9od_3-jAh95gHAK-a5oJTG9YWsDQACehsAApUowVNJqrNjQld6AjYE",
       
    ]
}
# =================================================================

# تعریف مراحل مکالمه ترند
ASKING_TREND_CATEGORY, SENDING_VIDEOS = range(7, 9)

async def ask_trend_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """پس از کلیک روی "چی ترنده؟"، دسته‌بندی‌ها را نمایش می‌دهد."""
    keyboard = [
        ["ویدیو های دیالوگی"],
        ["ویدیو های مینیمال بدون چهره"],
        ["ایده های فان"],
        [" بازگشت به منوی اصلی 🔙"]
    ]
    await update.message.reply_text(
        "بسیار خب! کدام دسته از ایده‌های ترند را می‌خواهی ببینی؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return ASKING_TREND_CATEGORY

async def send_videos_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویدیوهای مربوط به دسته انتخاب شده را ارسال می‌کند."""
    category = update.message.text
    video_ids = TREND_VIDEOS.get(category)

    if not video_ids or "FILE_ID" in video_ids[0]:
        await update.message.reply_text("متاسفانه هنوز ویدیویی برای این دسته تعریف نشده است. لطفاً دسته دیگری را انتخاب کنید.")
        return ASKING_TREND_CATEGORY

    await update.message.reply_text(f"حتماً! این هم چند نمونه از ترندهای دسته «{category}»:", reply_markup=ReplyKeyboardRemove())

    for video_id in video_ids:
        try:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video_id)
        except Exception as e:
            logger.error(f"Could not send video with id {video_id}. Error: {e}")
            await update.message.reply_text(f"متاسفانه در ارسال یکی از ویدیوها مشکلی پیش آمد.")

    # پس از اتمام کار، کاربر را به منوی اصلی برمیگردانیم
    # برای این کار، باید تابع start از فایل اصلی را فراخوانی کنیم
    # این کار در فایل اصلی handler انجام خواهد شد.
    return ConversationHandler.END
