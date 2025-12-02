"""
AI Post Optimizer - بهینه‌سازی پست با Liara AI
"""
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# پرامپت ثابت و ساختاردهی شده
PROMPT_TEMPLATE = """پست تلگرام رو بهینه کن.

کارها:
1. تیتر جذاب با ایموجی
2. قیمت‌ها رو بولد کن: **۱۵۰ یورو**
3. تاریخ‌ها رو بولد کن: **۱۱ آذر**
4. حذف کن: یوزرنیم (@)، لینک، فوتر کانال (Instagram/Telegram/YouTube)
5. فشرده بمونه، طولانی نکن
6. فقط فارسی بنویس

{user_post_text}"""


class AIOptimizer:
    """کلاس برای بهینه‌سازی پست‌ها با Liara AI"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize AI Optimizer
        
        Args:
            api_key: Liara API key
            base_url: Liara base URL
        """
        try:
            if not api_key or not base_url:
                logger.error("API key or base URL not provided")
                self.client = None
                return
                
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )
            logger.info("Liara AI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Liara AI client: {e}")
            self.client = None
    
    def optimize_post(self, raw_content: str) -> tuple[bool, str]:
        """
        بهینه‌سازی محتوای پست
        
        Args:
            raw_content: محتوای خام پست
            
        Returns:
            tuple: (success: bool, optimized_text: str)
        """
        if not self.client:
            return False, "❌ خطا: اتصال به سرویس هوش مصنوعی برقرار نیست."
        
        if not raw_content or len(raw_content.strip()) < 10:
            return False, "❌ متن ورودی خیلی کوتاه است. لطفاً محتوای بیشتری ارسال کنید."
        
        try:
            # ساخت پرامپت نهایی
            final_prompt = PROMPT_TEMPLATE.format(user_post_text=raw_content)
            
            logger.info(f"Sending request to Liara AI for optimization (length: {len(raw_content)})")
            
            # ارسال به Liara AI
            completion = self.client.chat.completions.create(
                model='openai/gpt-4o-mini',
                messages=[
                    {
                        'role': 'user',
                        'content': final_prompt
                    }
                ]
            )
            
            optimized_text = completion.choices[0].message.content.strip()
            
            # تبدیل ** به <b> (چون مدل گاهی از مارک‌داون استفاده می‌کنه)
            import re
            optimized_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', optimized_text)
            optimized_text = re.sub(r'__(.+?)__', r'<i>\1</i>', optimized_text)
            
            # حذف فوتر کانال‌ها
            optimized_text = re.sub(r'➖+.*?➖+', '', optimized_text, flags=re.DOTALL)
            optimized_text = re.sub(r'🌐\s*Instagram.*', '', optimized_text, flags=re.IGNORECASE)
            optimized_text = re.sub(r'🔵\s*Telegram.*', '', optimized_text, flags=re.IGNORECASE)
            optimized_text = re.sub(r'🎞\s*YouTube.*', '', optimized_text, flags=re.IGNORECASE)
            optimized_text = re.sub(r'\n{3,}', '\n\n', optimized_text)  # حذف خطوط خالی اضافی
            optimized_text = optimized_text.strip()
            
            logger.info(f"Successfully optimized post (output length: {len(optimized_text)})")
            
            return True, optimized_text
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error in Liara AI API call: {error_str}")
            
            # بررسی خطای rate limit
            if '429' in error_str or 'rate_limit' in error_str.lower():
                return False, (
                    "⚠️ محدودیت تعداد درخواست.\n\n"
                    "💡 لطفاً چند لحظه صبر کنید و دوباره تلاش کنید."
                )
            
            # بررسی خطای authentication
            if '401' in error_str or 'unauthorized' in error_str.lower():
                return False, (
                    "❌ خطای احراز هویت.\n\n"
                    "لطفاً API Key را بررسی کنید."
                )
            
            return False, f"❌ خطا در پردازش هوش مصنوعی:\n{error_str[:200]}"
    
    def is_available(self) -> bool:
        """بررسی در دسترس بودن سرویس"""
        return self.client is not None
