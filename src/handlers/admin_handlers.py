import logging
import os
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from src.utils.validators import admin_only
from src.utils.keyboards import admin_panel_keyboard, back_to_admin_panel_keyboard
from src.database.database import DBManager

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Conversation States ---
(   MANAGE_POST_TYPES,
    ADD_POST_TYPE_NAME,
    ADD_POST_TYPE_BANNER,
    DELETE_POST_TYPE_SELECT,
) = range(4)

# --- Main Admin Panel ---
@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the main admin panel."""
    await update.message.reply_text(
        text="به پنل مدیریت خوش آمدید.", reply_markup=admin_panel_keyboard()
    )
    return MANAGE_POST_TYPES

# --- View Post Types ---
@admin_only
async def view_post_types(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays a list of current post types."""
    query = update.callback_query
    await query.answer()

    db = DBManager()
    try:
        post_types = db.get_post_types()
        
        if not post_types:
            text = "هیچ نوع پستی تعریف نشده است."
        else:
            text = "انواع پست موجود:\n\n"
            text += "\n".join([f"- {pt.name}" for pt in post_types])
    finally:
        db.close()

    await query.edit_message_text(text=text, reply_markup=back_to_admin_panel_keyboard())
    return MANAGE_POST_TYPES

# --- Add Post Type --- 
@admin_only
async def add_post_type_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the process of adding a new post type."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="لطفاً نام نوع پست جدید را وارد کنید:")
    return ADD_POST_TYPE_NAME

@admin_only
async def add_post_type_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the name for the new post type and asks for the banner."""
    post_type_name = update.message.text.strip()
    context.user_data["new_post_type_name"] = post_type_name
    logger.info(f"Admin {update.effective_user.id} is adding a new post type named '{post_type_name}'.")
    await update.message.reply_text("نام دریافت شد. اکنون لطفاً بنر مربوط به این نوع پست را آپلود کنید (به صورت عکس).")
    return ADD_POST_TYPE_BANNER

@admin_only
async def add_post_type_banner_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the banner, saves it, and adds the new post type to the database."""
    if not update.message.photo:
        await update.message.reply_text("لطفاً یک عکس ارسال کنید.")
        return ADD_POST_TYPE_BANNER

    post_type_name = context.user_data.get("new_post_type_name")
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Ensure banner directory exists
    os.makedirs("data/banners", exist_ok=True)
    banner_path = f"data/banners/{post_type_name}.jpg"

    await file.download_to_drive(banner_path)
    logger.info(f"Banner for '{post_type_name}' saved to {banner_path}.")

    db = DBManager()
    try:
        if db.add_post_type(post_type_name):
            await update.message.reply_text(
                f"نوع پست '{post_type_name}' با موفقیت اضافه شد.",
                reply_markup=admin_panel_keyboard(),
            )
            logger.info(f"Post type '{post_type_name}' added to the database.")
        else:
            await update.message.reply_text(
                f"خطا: نوع پستی با نام '{post_type_name}' از قبل وجود دارد.",
                reply_markup=admin_panel_keyboard(),
            )
    finally:
        db.close()

    context.user_data.clear()
    return MANAGE_POST_TYPES

# --- Delete Post Type ---
@admin_only
async def delete_post_type_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows a list of post types to delete."""
    query = update.callback_query
    await query.answer()
    
    db = DBManager()
    try:
        post_types = db.get_post_types()
        if not post_types:
            await query.edit_message_text("هیچ نوع پستی برای حذف وجود ندارد.", reply_markup=back_to_admin_panel_keyboard())
            return MANAGE_POST_TYPES
    finally:
        db.close()
    
    await query.edit_message_text(
        "لطفاً نام دقیق نوع پستی که می‌خواهید حذف کنید را وارد نمایید.",
        reply_markup=back_to_admin_panel_keyboard()
    )
    return DELETE_POST_TYPE_SELECT

@admin_only
async def delete_post_type_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Deletes the selected post type."""
    post_type_name = update.message.text.strip()
    db = DBManager()
    
    try:
        if db.delete_post_type(post_type_name):
            # Also delete the banner file
            banner_path = f"data/banners/{post_type_name}.jpg"
            if os.path.exists(banner_path):
                os.remove(banner_path)
                logger.info(f"Banner file {banner_path} deleted.")

            await update.message.reply_text(
                f"نوع پست '{post_type_name}' با موفقیت حذف شد.",
                reply_markup=admin_panel_keyboard()
            )
            logger.info(f"Admin {update.effective_user.id} deleted post type '{post_type_name}'.")
        else:
            await update.message.reply_text(
                f"نوع پستی با نام '{post_type_name}' یافت نشد.",
                reply_markup=admin_panel_keyboard()
            )
    finally:
        db.close()
        
    return MANAGE_POST_TYPES

# --- Back and Cancel ---
@admin_only
async def back_to_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns to the main admin menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("پنل مدیریت:", reply_markup=admin_panel_keyboard())
    return MANAGE_POST_TYPES

async def cancel_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the current admin action and returns to the main menu."""
    await update.message.reply_text("عملیات لغو شد.", reply_markup=admin_panel_keyboard())
    context.user_data.clear()
    return MANAGE_POST_TYPES


# --- Admin Conversation Handler ---
admin_management_handler = ConversationHandler(
    entry_points=[CommandHandler("admin", admin_panel)],
    states={
        MANAGE_POST_TYPES: [
            CallbackQueryHandler(view_post_types, pattern="^view_post_types$"),
            CallbackQueryHandler(add_post_type_start, pattern="^add_post_type$"),
            CallbackQueryHandler(delete_post_type_start, pattern="^delete_post_type$"),
            CallbackQueryHandler(back_to_admin_menu, pattern="^back_to_admin_menu$"),
        ],
        ADD_POST_TYPE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_post_type_name_received)],
        ADD_POST_TYPE_BANNER: [MessageHandler(filters.PHOTO, add_post_type_banner_received)],
        DELETE_POST_TYPE_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_post_type_received)],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_admin_action, pattern="^cancel$"),
        MessageHandler(filters.Regex('^❌ لغو$'), cancel_admin_action)
    ],
    allow_reentry=True,
    per_message=False
)
