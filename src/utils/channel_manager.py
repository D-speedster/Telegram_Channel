"""
Channel Manager - مدیریت چند کانال
"""

# تعریف کانال‌ها
CHANNELS = {
    'film': {
        'name': '🎬 کانال فیلم',
        'id': 'FILM_CHANNEL_ID',  # از .env خوانده می‌شود
        'link': 'https://t.me/Film_Too_Film',
        'emoji': '🎬'
    },
    'italia': {
        'name': '🇮🇹 کانال ایتالیا',
        'id': 'ITALIA_CHANNEL_ID',  # از .env خوانده می‌شود
        'link': 'https://t.me/Italia_Channel',  # لینک واقعی را بعداً تنظیم کنید
        'emoji': '🇮🇹'
    }
}

def get_channel_info(channel_key: str) -> dict:
    """دریافت اطلاعات کانال"""
    return CHANNELS.get(channel_key, {})

def get_all_channels() -> dict:
    """دریافت لیست تمام کانال‌ها"""
    return CHANNELS

def get_channel_link(channel_key: str) -> str:
    """دریافت لینک کانال"""
    channel = get_channel_info(channel_key)
    return channel.get('link', '')
