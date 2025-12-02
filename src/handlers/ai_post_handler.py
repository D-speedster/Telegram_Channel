"""
AI Post Handler - مدیریت ساخت پست با AI
"""
import logging
import re
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from src.utils.validators import admin_only
from src.utils.keyboards import confirm_keyboard, main_menu_keyboard
from src.utils.ai_optimizer import AIOptimizer
from src.config import LIARA_API_KEY, LIARA_BASE_URL

logger = logging.getLogger(__name__)

# States
WAITING_FOR_POST, WAITING_FOR_CONFIRMATION, WAITING_FOR_TAG = range(3)

# Initialize AI Optimizer
ai_optimizer = AIOptimizer(api_key=LIARA_API_KEY, base_url=LIARA_BASE_URL)


def remove_tags_and_usernames(text: str) -> str:
    """حذف یوزرنیم‌ها و تگ‌ها از متن"""
    # حذف @username
    text = re.sub(r'@\w+', '', text)
    # حذف لینک‌های تلگرام
    text = re.sub(r'https?://t\.me/\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)
    # حذف خطوط خالی اضافی
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


@admin_only
async def start_ai_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع فرآیند ساخت پست با AI"""
    
    if not ai_optimizer.is_available():
        await update.message.reply_text(
            "❌ سرویس هوش مصنوعی در دسترس نیست.",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END
    
    logger.info(f"Admin {update.effective_user.id} started AI post creation")
    
    await update.message.reply_text(
        "🤖 ساخت پست هوشمند\n\n"
        "📤 پست خود را فوروارد یا ارسال کنید.\n"
        "(متن، عکس یا ویدیو با کپشن)\n\n"
        "برای لغو: /cancel"
    )
    
    return WAITING_FOR_POST


@admin_only
async def receive_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت پست و بهینه‌سازی با AI"""
    
    message = update.message
    raw_text = None
    media_type = None
    media_id = None
    
    if message.photo:
        media_type = 'photo'
        media_id = message.photo[-1].file_id
        raw_text = message.caption
    elif message.video:
        media_type = 'video'
        media_id = message.video.file_id
        raw_text = message.caption
    elif message.animation:
        media_type = 'animation'
        media_id = message.animation.file_id
        raw_text = message.caption
    elif message.document:
        media_type = 'document'
        media_id = message.document.file_id
        raw_text = message.caption
    elif message.text:
        media_type = 'text'
        raw_text = message.text
    
    if not raw_text:
        await message.reply_text("❌ پست باید متن یا کپشن داشته باشه.")
        return WAITING_FOR_POST
    
    context.user_data['media_type'] = media_type
    context.user_data['media_id'] = media_id
    context.user_data['raw_text'] = raw_text
    
    processing_msg = await message.reply_text("⏳ در حال بهینه‌سازی...")
    
    success, optimized_text = ai_optimizer.optimize_post(raw_text)
    
    await processing_msg.delete()
    
    if not success:
        await message.reply_text(optimized_text, reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    
    # حذف تگ‌ها و یوزرنیم‌ها
    optimized_text = remove_tags_and_usernames(optimized_text)
    context.user_data['optimized_text'] = optimized_text
    
    await message.reply_text("✅ بهینه شد!\n\n📋 پیش‌نمایش:")
    
    # ارسال پیش‌نمایش
    try:
        if media_type == 'photo':
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=media_id,
                caption=optimized_text, parse_mode='HTML', reply_markup=confirm_keyboard()
            )
        elif media_type == 'video':
            await context.bot.send_video(
                chat_id=update.effective_chat.id, video=media_id,
                caption=optimized_text, parse_mode='HTML', reply_markup=confirm_keyboard()
            )
        elif media_type == 'animation':
            await context.bot.send_animation(
                chat_id=update.effective_chat.id, animation=media_id,
                caption=optimized_text, parse_mode='HTML', reply_markup=confirm_keyboard()
            )
        elif media_type == 'document':
            await context.bot.send_document(
                chat_id=update.effective_chat.id, document=media_id,
                caption=optimized_text, parse_mode='HTML', reply_markup=confirm_keyboard()
            )
        else:
            await message.reply_text(optimized_text, parse_mode='HTML', reply_markup=confirm_keyboard())
    except Exception as e:
        logger.error(f"Error sending preview: {e}")
        # اگر HTML مشکل داشت، بدون parse_mode بفرست
        await message.reply_text(optimized_text, reply_markup=confirm_keyboard())
    
    return WAITING_FOR_CONFIRMATION


@admin_only
async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت تأیید"""
    
    query = update.callback_query
    await query.answer()
    
    if query.data == 'ai_cancel':
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ لغو شد.",
            reply_markup=main_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    # تأیید شد - درخواست تگ
    await query.edit_message_reply_markup(reply_markup=None)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🏷 تگ یا امضای زیر پست رو بفرست:\n\n"
             "مثال:\n"
             "🔗 @MyChannel | @MyBot\n\n"
             "یا بزن /skip برای بدون تگ"
    )
    
    return WAITING_FOR_TAG


@admin_only
async def receive_tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت تگ و ارسال پست نهایی"""
    
    tag = update.message.text
    
    # اگر skip زد
    if tag == '/skip':
        tag = None
    
    media_type = context.user_data.get('media_type')
    media_id = context.user_data.get('media_id')
    optimized_text = context.user_data.get('optimized_text')
    
    # اضافه کردن تگ
    if tag:
        final_text = f"{optimized_text}\n\n{tag}"
    else:
        final_text = optimized_text
    
    await update.message.reply_text("✅ پست نهایی:")
    
    # ارسال پست نهایی
    try:
        if media_type == 'photo':
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=media_id,
                caption=final_text, parse_mode='HTML'
            )
        elif media_type == 'video':
            await context.bot.send_video(
                chat_id=update.effective_chat.id, video=media_id,
                caption=final_text, parse_mode='HTML'
            )
        elif media_type == 'animation':
            await context.bot.send_animation(
                chat_id=update.effective_chat.id, animation=media_id,
                caption=final_text, parse_mode='HTML'
            )
        elif media_type == 'document':
            await context.bot.send_document(
                chat_id=update.effective_chat.id, document=media_id,
                caption=final_text, parse_mode='HTML'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=final_text, parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error sending final: {e}")
        # بدون HTML
        if media_type == 'text':
            await context.bot.send_message(chat_id=update.effective_chat.id, text=final_text)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ آماده فوروارد!",
        reply_markup=main_menu_keyboard()
    )
    
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_ai_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو"""
    await update.message.reply_text("❌ لغو شد.", reply_markup=main_menu_keyboard())
    context.user_data.clear()
    return ConversationHandler.END


# Conversation Handler
ai_post_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^➕ ساخت پست هوشمند$'), start_ai_post)],
    states={
        WAITING_FOR_POST: [
            MessageHandler(
                (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL) 
                & ~filters.COMMAND,
                receive_post
            )
        ],
        WAITING_FOR_CONFIRMATION: [
            CallbackQueryHandler(handle_confirmation, pattern='^(ai_confirm|ai_cancel)$')
        ],
        WAITING_FOR_TAG: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tag),
            MessageHandler(filters.Regex('^/skip$'), receive_tag)
        ]
    },
    fallbacks=[
        MessageHandler(filters.Regex('^/cancel$'), cancel_ai_post),
        MessageHandler(filters.Regex('^❌ لغو$'), cancel_ai_post)
    ],
    allow_reentry=True,
    per_message=False
)
