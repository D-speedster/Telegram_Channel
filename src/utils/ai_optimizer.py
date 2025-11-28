"""
AI Post Optimizer - بهینه‌سازی پست با Liara AI
"""
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# پرامپت ثابت و ساختاردهی شده
PROMPT_TEMPLATE = """ویراستار تلگرام هستی. متن رو برای کانال بهینه کن.

ساختار:
1. ایموجی + تیتر بولد کوتاه
2. خط خالی
3. متن روان و خودمونی (نه خیلی رسمی)
4. لیست‌ها با 🔹

فرمت HTML:
- بولد: <b>متن</b>
- هرگز ** نزن

قوانین:
- لحن صمیمی و خودمونی (مثل گفتگو)
- محتوا رو تغییر نده
- غلط‌ها رو تصحیح کن
- خلاصه‌تر کن
- یوزرنیم‌ها و تگ‌های @ رو حذف کن
- لینک‌ها و آیدی کانال‌ها رو حذف کن

فقط خروجی:

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
