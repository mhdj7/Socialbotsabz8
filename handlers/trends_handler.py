# handlers/trends_handler.py
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

# تنظیمات لاگ
logger = logging.getLogger(__name__)

# =================================================================
# >> شناسه‌های ویدیوهای خود را در اینجا وارد کنید <<
TREND_VIDEOS = {
    "ویدیو های دیالوگی": [
        "FILE_ID_DIALOGUE_1", 
        "FILE_ID_DIALOGUE_2"
    ],
    "ویدیو های مینیمال بدون چهره": [
        "FILE_ID_MINIMAL_1",
        "FILE_ID_MINIMAL_2"
    ],
    "ایده های فان": [
        "FILE_ID_FUN_1",
        "FILE_ID_FUN_2"
    ]
}
# =================================================================

# تعریف مراحل مکالمه ترند
ASKING_TREND_CATEGORY = range(10, 11)

async def ask_trend_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """پس از کلیک روی "چی ترنده؟"، دسته‌بندی‌ها را نمایش می‌دهد."""
    keyboard = [
        ["ویدیو های دیالوگی"],
        ["ویدیو های مینیمال بدون چهره"],
        ["ایده های فان"],
        ["بازگشت به منوی اصلی 🔙"]
    ]
    await update.message.reply_text(
        "بسیار خب! کدام دسته از ایده‌های ترند را می‌خواهی ببینی؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return ASKING_TREND_CATEGORY

async def send_videos_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ویدیوهای مربوط به دسته انتخاب شده را ارسال می‌کند و به منوی اصلی برمیگردد."""
    # وارد کردن محلی برای جلوگیری از خطای وابستگی چرخه‌ای
    from .scenario_handler import start

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

    # رفع باگ: به جای پایان دادن به مکالمه، به حالت شروع بازمیگردیم
    return await start(update, context)
