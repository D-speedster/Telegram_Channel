"""
AI Post Optimizer - بهینه‌سازی پست با Gemini AI
"""
import logging
from google import genai

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
    """کلاس برای بهینه‌سازی پست‌ها با Gemini AI"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize AI Optimizer
        
        Args:
            api_key: Gemini API key (optional, can be set via GEMINI_API_KEY env var)
        """
        try:
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                # خواندن از متغیر محیطی
                self.client = genai.Client()
            logger.info("Gemini AI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {e}")
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
            
            logger.info(f"Sending request to Gemini for optimization (length: {len(raw_content)})")
            
            # ارسال به Gemini
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=final_prompt
            )
            
            optimized_text = response.text.strip()
            
            logger.info(f"Successfully optimized post (output length: {len(optimized_text)})")
            
            return True, optimized_text
            
        except Exception as e:
            logger.error(f"Error in Gemini API call: {e}")
            return False, f"❌ خطا در پردازش هوش مصنوعی: {str(e)}"
    
    def is_available(self) -> bool:
        """بررسی در دسترس بودن سرویس"""
        return self.client is not None
