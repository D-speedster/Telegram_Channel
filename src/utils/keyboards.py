from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import List

# --- Main Menu Keyboard ---
def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Returns the main menu keyboard for admins."""
    keyboard = [
        ["➕ ساخت پست هوشمند"],
        ["🎬 پست فیلم"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# --- Channel Selection Keyboard (Legacy) ---
def channel_selection_keyboard() -> ReplyKeyboardMarkup:
    """Returns keyboard for selecting channel."""
    return main_menu_keyboard()

# --- Channel Menu Keyboard (Legacy) ---
def channel_menu_keyboard(channel_name: str = None) -> ReplyKeyboardMarkup:
    """Returns menu keyboard - now same as main menu."""
    return main_menu_keyboard()

# --- Dynamic Post Types Keyboard ---
def post_types_keyboard(post_types: List[str]) -> InlineKeyboardMarkup:
    """
    Generates a dynamic inline keyboard from a list of post types.
    Each post type will have a callback_data like 'post_type_text', 'post_type_photo'.
    """
    keyboard = [[InlineKeyboardButton(pt, callback_data=f"post_type_{pt}")] for pt in post_types]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main_menu")])
    return InlineKeyboardMarkup(keyboard)

# --- Confirmation Keyboard ---
def confirm_keyboard() -> InlineKeyboardMarkup:
    """Returns a confirmation keyboard (Yes/No)."""
    keyboard = [
        [InlineKeyboardButton("✅ ارسال شود", callback_data="confirm_send"),
         InlineKeyboardButton("❌ خیر", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Admin Panel Keyboard ---
def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """
    Returns the keyboard for the admin panel with various management options.
    """
    keyboard = [
        [InlineKeyboardButton("👁️ مشاهده انواع پست", callback_data="view_post_types")],
        [InlineKeyboardButton("➕ افزودن نوع پست", callback_data="add_post_type")],
        [InlineKeyboardButton("🗑️ حذف نوع پست", callback_data="delete_post_type")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Returns a keyboard with a button to go back to the admin menu."""
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data="back_to_admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)