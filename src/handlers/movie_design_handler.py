import logging
import re
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from src.utils.validators import admin_only
from src.utils.keyboards import confirm_keyboard, main_menu_keyboard

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Conversation States ---
WAITING_FOR_MOVIE_POST, WAITING_FOR_CONFIRM_FIRST, WAITING_FOR_FILE, WAITING_FOR_FINAL_CONFIRM = range(4)

# --- Helper Functions ---
def extract_movie_info(caption: str) -> dict:
    """استخراج اطلاعات فیلم از کپشن"""
    info = {
        'name': '',
        'genre': '',
        'language': '',
        'score': '',
        'awards': '',
        'actors': [],
        'duration': '',
        'summary': '',
        'year': '',
        'country': '',
        'quality': '720p'  # مقدار پیش‌فرض
    }
    
    # استخراج نام فیلم و سال
    name_line_match = re.search(r'🎥فیلم\s*(.+?)(?:\n|$)', caption)
    if name_line_match:
        full_name = name_line_match.group(1).strip()
        
        # استخراج سال (اولین عدد 4 رقمی)
        year_match = re.search(r'\((\d{4})', full_name)
        if year_match:
            info['year'] = year_match.group(1)
        
        # استخراج نام انگلیسی
        # فرمت: (April..s Daug..hter Las hij..as de Ab..ril (2017 (دختر ماه آوریل)
        name_clean = full_name.lstrip('(').strip()
        
        # حذف قسمت (سال) و بعد از آن
        if year_match:
            year_pos = name_clean.find(f"({info['year']}")
            if year_pos > 0:
                name_clean = name_clean[:year_pos].strip()
        
        # حذف نقطه‌های اضافی
        name_clean = re.sub(r'\.\.', '', name_clean)
        info['name'] = name_clean.strip()
    
    # استخراج ژانر
    genre_match = re.search(r'📽ژانر:\s*(.+?)(?:\n|$)', caption)
    if genre_match:
        info['genre'] = genre_match.group(1).strip()
    
    # استخراج زبان (پشتیبانی از 📄 و 📃)
    lang_match = re.search(r'[📄📃]زبان:\s*(.+?)(?:\n|$)', caption)
    if lang_match:
        info['language'] = lang_match.group(1).strip()
    
    # استخراج امتیاز (با پشتیبانی از اعداد فارسی و ایموجی‌های مختلف)
    score_match = re.search(r'[⭐️⭐]امتیاز\s*([۰-۹0-9\.]+)\s*از\s*([۰-۹0-9]+)', caption)
    if score_match:
        score = score_match.group(1).strip()
        total = score_match.group(2).strip()
        logger.info(f"Score extracted: {score} از {total}")
        # تبدیل اعداد فارسی به انگلیسی
        persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
        score = score.translate(persian_to_english)
        total = total.translate(persian_to_english)
        info['score'] = f"{score}/{total}"
        logger.info(f"Score converted: {info['score']}")
    else:
        logger.warning("Score not found in caption")
    
    # استخراج جوایز
    awards_match = re.search(r'🎁جوایز:\s*(.+?)(?:\n|$)', caption)
    if awards_match:
        info['awards'] = awards_match.group(1).strip()
    
    # استخراج بازیگران
    actors = re.findall(r'/([A-Za-z_]+)', caption)
    info['actors'] = actors
    
    # استخراج مدت زمان (با پشتیبانی از اعداد فارسی و ایموجی ⌛️)
    duration_match = re.search(r'[⏳⌛️]مدت زمان:\s*(.+?)(?:\n|$)', caption)
    if duration_match:
        duration = duration_match.group(1).strip()
        # تبدیل اعداد فارسی به انگلیسی
        persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
        info['duration'] = duration.translate(persian_to_english)
    
    # استخراج کیفیت (Quality)
    quality_match = re.search(r'[🎬📹🎥]کیفیت:\s*(.+?)(?:\n|$)', caption)
    if not quality_match:
        quality_match = re.search(r'Quality:\s*(.+?)(?:\n|$)', caption)
    if not quality_match:
        # جستجو برای الگوهای رایج کیفیت
        quality_patterns = [
            r'\b(4K|2160p|1080p|720p|480p|360p)\b',
            r'\b(BluRay|BRRip|WEB-DL|WEBRip|HDRip)\b'
        ]
        for pattern in quality_patterns:
            quality_match = re.search(pattern, caption, re.IGNORECASE)
            if quality_match:
                info['quality'] = quality_match.group(1)
                break
    else:
        info['quality'] = quality_match.group(1).strip()
    
    # استخراج خلاصه داستان
    summary_match = re.search(r'خلاصه داستان:\s*(.+?)$', caption, re.DOTALL)
    if summary_match:
        info['summary'] = summary_match.group(1).strip()
    
    return info

def create_formatted_caption(info: dict) -> str:
    """ساخت کپشن فرمت شده بر اساس قالب"""
    caption = f"""Download 🔞#Film_Nights🔞

⬛️ Name: {info['name']}
🟨 Data Release: {info['year']}
🟥 Score IMDB: 《{info['score']}》
🟩 Country: {info['country'] if info['country'] else '🇺🇸 USA'}
🟪 Time: {info['duration']}
🟫 Genre: 《{info['genre']}》

{info['summary']}

🔗 https://t.me/Film_Maamnooe"""
    
    return caption

def create_file_caption(info: dict) -> str:
    """ساخت کپشن برای فایل"""
    quality = info.get('quality', '720p')
    caption = f"""🟧 {info['name']}
🟥 Quality: {quality}
🟦 Language: 《زیرنویس چسبیده》

🔗 https://t.me/Film_Maamnooe"""
    
    return caption

# --- Handler Functions ---

@admin_only
async def start_movie_design(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع فرآیند دیزاین پست فیلم"""
    logger.info(f"Admin {update.effective_user.id} started movie design.")
    
    await update.message.reply_text(
        "📽 دیزاین پست فیلم\n\n"
        "لطفاً پست فیلم خود را ارسال کنید.\n"
        "پست باید شامل تصویر و کپشن با اطلاعات فیلم باشد."
    )
    return WAITING_FOR_MOVIE_POST

@admin_only
async def receive_movie_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت پست فیلم و استخراج اطلاعات"""
    if not update.message.photo:
        await update.message.reply_text(
            "❌ لطفاً یک پست با تصویر ارسال کنید.\n"
            "پست باید شامل تصویر و کپشن باشد."
        )
        return WAITING_FOR_MOVIE_POST
    
    if not update.message.caption:
        await update.message.reply_text(
            "❌ لطفاً کپشن پست را هم ارسال کنید.\n"
            "کپشن باید شامل اطلاعات فیلم باشد."
        )
        return WAITING_FOR_MOVIE_POST
    
    # ذخیره تصویر
    photo = update.message.photo[-1]
    context.user_data['movie_photo'] = photo.file_id
    
    # استخراج اطلاعات
    caption = update.message.caption
    movie_info = extract_movie_info(caption)
    
    # ذخیره اطلاعات
    context.user_data['movie_info'] = movie_info
    
    # ساخت کپشن فرمت شده
    formatted_caption = create_formatted_caption(movie_info)
    context.user_data['formatted_caption'] = formatted_caption
    
    # نمایش پیش‌نمایش
    await update.message.reply_photo(
        photo=photo.file_id,
        caption=f"📋 پیش‌نمایش پست اول:\n\n{formatted_caption}",
        reply_markup=confirm_keyboard()
    )
    
    logger.info(f"Admin {update.effective_user.id} submitted movie post for design.")
    return WAITING_FOR_CONFIRM_FIRST

@admin_only
async def handle_first_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت تأیید پست اول"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel_action':
        await query.edit_message_text("❌ عملیات لغو شد.")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="به منوی اصلی بازگشتید:",
            reply_markup=main_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    # تأیید شد، درخواست فایل
    await query.edit_message_reply_markup(reply_markup=None)
    
    movie_info = context.user_data.get('movie_info', {})
    file_caption = create_file_caption(movie_info)
    context.user_data['file_caption'] = file_caption
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ پست اول تأیید شد.\n\n"
             f"📋 کپشن پست دوم:\n\n{file_caption}\n\n"
             f"📁 حالا لطفاً فایل فیلم خود را ارسال کنید."
    )
    
    return WAITING_FOR_FILE

@admin_only
async def receive_movie_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت فایل فیلم"""
    if not update.message.document and not update.message.video:
        await update.message.reply_text(
            "❌ لطفاً فایل فیلم را ارسال کنید.\n"
            "فایل می‌تواند Document یا Video باشد."
        )
        return WAITING_FOR_FILE
    
    # ذخیره فایل
    if update.message.document:
        file_obj = update.message.document
        context.user_data['movie_file'] = file_obj.file_id
        context.user_data['file_type'] = 'document'
        context.user_data['file_name'] = file_obj.file_name
    else:
        file_obj = update.message.video
        context.user_data['movie_file'] = file_obj.file_id
        context.user_data['file_type'] = 'video'
        context.user_data['file_name'] = 'video.mp4'
    
    # نمایش پیش‌نمایش فایل با کپشن
    file_caption = context.user_data.get('file_caption')
    
    try:
        if context.user_data['file_type'] == 'document':
            await update.message.reply_document(
                document=context.user_data['movie_file'],
                caption=f"📋 پیش‌نمایش پست دوم:\n\n{file_caption}",
                reply_markup=confirm_keyboard()
            )
        else:
            await update.message.reply_video(
                video=context.user_data['movie_file'],
                caption=f"📋 پیش‌نمایش پست دوم:\n\n{file_caption}",
                reply_markup=confirm_keyboard()
            )
    except Exception as e:
        logger.error(f"Error showing file preview: {e}")
        await update.message.reply_text(
            f"📋 پیش‌نمایش پست دوم:\n\n{file_caption}\n\n"
            "✅ فایل دریافت شد.\n"
            "آیا می‌خواهید هر دو پست را دریافت کنید؟",
            reply_markup=confirm_keyboard()
        )
    
    logger.info(f"Admin {update.effective_user.id} submitted movie file.")
    return WAITING_FOR_FINAL_CONFIRM

@admin_only
async def handle_final_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت تأیید نهایی و ارسال به ادمین"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel_action':
        await query.edit_message_text("❌ عملیات لغو شد.")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="به منوی اصلی بازگشتید:",
            reply_markup=main_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    # ارسال به ادمین
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⏳ در حال آماده‌سازی پست‌ها..."
    )
    
    try:
        # ارسال پست اول (تصویر)
        photo_id = context.user_data.get('movie_photo')
        formatted_caption = context.user_data.get('formatted_caption')
        
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=formatted_caption
        )
        
        # ارسال پست دوم (فایل)
        file_id = context.user_data.get('movie_file')
        file_type = context.user_data.get('file_type')
        file_caption = context.user_data.get('file_caption')
        
        if file_type == 'document':
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file_id,
                caption=file_caption
            )
        else:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=file_id,
                caption=file_caption
            )
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ هر دو پست آماده شدند!\n\n"
                 "می‌توانید آنها را به کانال خود فوروارد کنید.",
            reply_markup=main_menu_keyboard()
        )
        
        logger.info(f"Admin {update.effective_user.id} successfully created movie posts.")
        
    except Exception as e:
        logger.error(f"Error creating movie posts: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ خطا در آماده‌سازی پست‌ها:\n{str(e)}",
            reply_markup=main_menu_keyboard()
        )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_movie_design(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو فرآیند دیزاین پست"""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ عملیات لغو شد.")
    else:
        await update.message.reply_text("❌ عملیات لغو شد.")
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="به منوی اصلی بازگشتید:",
        reply_markup=main_menu_keyboard()
    )
    
    context.user_data.clear()
    logger.info(f"User {update.effective_user.id} canceled movie design.")
    return ConversationHandler.END

# --- Conversation Handler ---
movie_design_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^🎬 دیزاین پست فیلم$'), start_movie_design)],
    states={
        WAITING_FOR_MOVIE_POST: [
            MessageHandler(filters.PHOTO, receive_movie_post)
        ],
        WAITING_FOR_CONFIRM_FIRST: [
            CallbackQueryHandler(handle_first_confirm, pattern='^(confirm_send|cancel_action)$')
        ],
        WAITING_FOR_FILE: [
            MessageHandler(filters.Document.ALL | filters.VIDEO, receive_movie_file)
        ],
        WAITING_FOR_FINAL_CONFIRM: [
            CallbackQueryHandler(handle_final_confirm, pattern='^(confirm_send|cancel_action)$')
        ]
    },
    fallbacks=[
        CallbackQueryHandler(cancel_movie_design, pattern='^cancel_action$'),
        MessageHandler(filters.Regex('^❌ لغو$'), cancel_movie_design)
    ],
    allow_reentry=True,
    per_message=False
)
