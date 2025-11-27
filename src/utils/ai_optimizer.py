"""
AI Post Optimizer - بهینه‌سازی پست با Liara AI
"""
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# پرامپت ثابت و ساختاردهی شده
PROMPT_TEMPLATE = """**نقش شما:** شما یک متخصص بازاریابی محتوا، ویراستار حرفه‌ای و کپی‌رایتر باتجربه در پلتفرم تلگرام هستید.

**هدف:** تبدیل محتوای خام و اولیه کاربر به یک پست کانال تلگرام فوق‌العاده جذاب، خوانا، کاربرپسند و بهینه شده با هدف افزایش تعامل (Engagement).

**دستورالعمل‌های جزئی:**
1.  **لحن و جذابیت:** لحن را به یک لحن دوستانه، صمیمی، مطمئن و انگیزشی تغییر دهید.
2.  **خوانایی و ساختار:** پاراگراف‌های طولانی را به جملات کوتاه تقسیم کنید.
3.  **اموجی و بولد:** از اموجی‌های مرتبط برای جذابیت بصری و از **بولد کردن (**...**)** کلمات کلیدی (حداقل ۵ مورد) استفاده کنید.
4.  **فراخوان به عمل (CTA):** در انتهای پست، یک فراخوان به عمل قوی و مرتبط اضافه کنید (مانند "نظر دهید" یا "برای دوستان فوروارد کنید").

**محتوای خام برای بهینه‌سازی:**
---
{user_post_text}
---

**محدودیت مدل:** خروجی شما باید تنها شامل متن بازنویسی شده نهایی باشد و هیچ توضیح، مقدمه یا پیامی را اضافه نکنید."""


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
