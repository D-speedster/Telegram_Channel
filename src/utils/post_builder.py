import logging
from telegram import Bot
from telegram.error import TelegramError
from typing import Optional

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def send_post_to_channel(bot: Bot, channel_id: str, photo_path: Optional[str], caption: str) -> bool:
    """
    Sends a post (photo with caption or just text) to the specified channel.

    Args:
        bot (Bot): The Telegram bot instance.
        channel_id (str): The ID of the target channel.
        photo_path (Optional[str]): The file path of the photo to send. None for text-only posts.
        caption (str): The text caption for the post.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    if not channel_id:
        logger.error("Channel ID is not configured.")
        return False
        
    try:
        if photo_path:
            with open(photo_path, 'rb') as photo_file:
                await bot.send_photo(
                    chat_id=channel_id,
                    photo=photo_file,
                    caption=caption,
                    parse_mode='HTML'
                )
        else:
            await bot.send_message(
                chat_id=channel_id,
                text=caption,
                parse_mode='HTML'
            )
        logger.info(f"Post successfully sent to channel {channel_id}.")
        return True
    except FileNotFoundError:
        logger.error(f"Error sending post: Photo file not found at {photo_path}")
        return False
    except TelegramError as e:
        logger.error(f"Telegram Error sending post to channel {channel_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending post to channel {channel_id}: {e}")
        return False
