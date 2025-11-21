from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging

# Import the list of admin IDs from the main config
from src.config import ADMIN_IDS

logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Checks if a user is one of the configured admins."""
    return user_id in ADMIN_IDS

def admin_only(func):
    """
    A decorator to restrict access to a handler to admins only.
    If the user is not an admin, it sends a notification and blocks access.
    """
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or not is_admin(user.id):
            logger.warning(f"Unauthorized access denied for user {user.id if user else 'Unknown'}.")
            if update.message:
                await update.message.reply_text("⛔️ متاسفم، شما اجازه دسترسی به این دستور را ندارید.")
            elif update.callback_query:
                await update.callback_query.answer("⛔️ شما اجازه دسترسی ندارید.", show_alert=True)
            return None
        return await func(update, context, *args, **kwargs)
    return wrapped