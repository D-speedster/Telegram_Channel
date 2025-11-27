"""
AI Post Handler - مدیریت ساخت پست با AI
"""
import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from src.utils.validators import admin_only
from src.utils.keyboards import confirm_keyboard, channel_menu_keyboard
from src.utils.ai_optimizer import AIOptimizer
from src.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# States
WAITING_FOR_RAW_CONTENT, WAITING_FOR_CONFIRMATION = range(2)

# Initialize AI Optimizer
ai_optimizer = AIOptimizer(api_key=GEMINI_API_KEY)


@admin_only
async def start_ai_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع فرآیند ساخت پست با AI"""
    
    # بررسی انتخاب کانال
    selected_channel = context.user_data.get('selected_channel')
    channel_name = context.user_data.get('channel_name', 'کانال')
    
    if not selected_channel:
        await update.message.reply_text(
            "⚠️ لطفاً ابتدا یک کانال انتخاب کنید.\n"
            "از منوی اصلی کانال مورد نظر را انتخاب کنید."
        )
        return ConversationHandler.END
    
    # بررسی در دسترس بودن AI
    if not ai_optimizer.is_available():
        await update.message.reply_text(
            "❌ سرویس هوش مصنوعی در دسترس نیست.\n"
            "لطفاً با مدیر سیستم تماس بگیرید.",
            reply_markup=channel_menu_keyboard(selected_channel)
        )
        return ConversationHandler.END
    
    logger.info(f"Admin {update.effective_user.id} started AI post creation for {channel_name}")
    
    await update.message.reply_text(
        f"🤖 ساخت پست هوشمند برای {channel_name}\n\n"
        "✍️ لطفاً محتوای خام پست خود را ارسال کنید.\n\n"
        "💡 نکته: هر چه محتوای شما کامل‌تر باشد، نتیجه بهتری خواهید گرفت.\n\n"
        "برای لغو: /cancel"
    )
    
    return WAITING_FOR_RAW_CONTENT


@admin_only
async def receive_raw_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت محتوای خام و بهینه‌سازی با AI"""
    
    raw_content = update.message.text
    
    # نمایش پیام در حال پردازش
    processing_msg = await update.message.reply_text(
        "⏳ در حال بهینه‌سازی پست با هوش مصنوعی...\n"
        "لطفاً چند لحظه صبر کنید."
    )
    
    # بهینه‌سازی با AI
    success, optimized_text = ai_optimizer.optimize_post(raw_content)
    
    # حذف پیام در حال پردازش
    await processing_msg.delete()
    
    if not success:
        await update.message.reply_text(
            optimized_text,  # پیام خطا
            reply_markup=channel_menu_keyboard(context.user_data.get('selected_channel'))
        )
        return ConversationHandler.END
    
    # ذخیره پست بهینه شده
    context.user_data['optimized_post'] = optimized_text
    context.user_data['raw_post'] = raw_content
    
    # نمایش پیش‌نمایش
    await update.message.reply_text(
        "✅ پست شما بهینه‌سازی شد!\n\n"
        "📋 پیش‌نمایش:\n"
        "━━━━━━━━━━━━━━━━"
    )
    
    await update.message.reply_text(
        optimized_text,
        reply_markup=confirm_keyboard()
    )
    
    logger.info(f"Admin {update.effective_user.id} received optimized post")
    
    return WAITING_FOR_CONFIRMATION


@admin_only
async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت تأیید یا لغو پست"""
    
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel_action':
        await query.edit_message_text("❌ عملیات لغو شد.")
        
        selected_channel = context.user_data.get('selected_channel')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="به منوی کانال بازگشتید:",
            reply_markup=channel_menu_keyboard(selected_channel)
        )
        
        context.user_data.pop('optimized_post', None)
        context.user_data.pop('raw_post', None)
        
        return ConversationHandler.END
    
    # تأیید شد - ارسال پست نهایی
    await query.edit_message_reply_markup(reply_markup=None)
    
    optimized_post = context.user_data.get('optimized_post')
    selected_channel = context.user_data.get('selected_channel')
    channel_name = context.user_data.get('channel_name', 'کانال')
    
    # دریافت لینک کانال
    from src.utils.channel_manager import get_channel_info
    channel_info = get_channel_info(selected_channel)
    channel_link = channel_info.get('link', '')
    
    # اضافه کردن لینک کانال به انتهای پست
    final_post = f"{optimized_post}\n\n🔗 {channel_link}"
    
    # ارسال پست نهایی به ادمین
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ پست نهایی آماده است:\n"
             "━━━━━━━━━━━━━━━━"
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=final_post
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ پست برای {channel_name} آماده شد!\n\n"
             "می‌توانید آن را به کانال خود فوروارد کنید.",
        reply_markup=channel_menu_keyboard(selected_channel)
    )
    
    logger.info(f"Admin {update.effective_user.id} confirmed AI-optimized post")
    
    # پاک کردن داده‌ها
    context.user_data.pop('optimized_post', None)
    context.user_data.pop('raw_post', None)
    
    return ConversationHandler.END


async def cancel_ai_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو فرآیند ساخت پست"""
    
    selected_channel = context.user_data.get('selected_channel')
    
    await update.message.reply_text(
        "❌ عملیات لغو شد.",
        reply_markup=channel_menu_keyboard(selected_channel)
    )
    
    context.user_data.pop('optimized_post', None)
    context.user_data.pop('raw_post', None)
    
    logger.info(f"User {update.effective_user.id} canceled AI post creation")
    
    return ConversationHandler.END


# Conversation Handler
ai_post_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex('^➕ ساخت پست جدید$'), start_ai_post)],
    states={
        WAITING_FOR_RAW_CONTENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_raw_content)
        ],
        WAITING_FOR_CONFIRMATION: [
            CallbackQueryHandler(handle_confirmation, pattern='^(confirm_send|cancel_action)$')
        ]
    },
    fallbacks=[
        MessageHandler(filters.Regex('^/cancel$'), cancel_ai_post),
        MessageHandler(filters.Regex('^❌ لغو$'), cancel_ai_post)
    ],
    allow_reentry=True,
    per_message=False
)
