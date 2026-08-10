import asyncio
import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from playwright.async_api import async_playwright

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7303980265:AAFjXBVO9kwB-9F5MrwAtRBCUvMqM3yANkw")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك! أرسل لي البريد الإلكتروني الخاص بك للبدء بتنفيذ العملية تلقائياً."
    )

async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_email = update.message.text.strip()
    
    if "@" not in user_email or "." not in user_email:
        await update.message.reply_text("الرجاء إدخال بريد إلكتروني صحيح.")
        return

    status_msg = await update.message.reply_text("جاري فتح المتصفح التلقائي على السيرفر...")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context_browser = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context_browser.new_page()

            await status_msg.edit_text("جاري فتح الموقع والبدء بالتسجيل...")
            await page.goto("https://internshala.com/", timeout=60000)
            await page.wait_for_timeout(3000)

            screenshot_path = f"status_{update.effective_user.id}.png"
            await page.screenshot(path=screenshot_path)
            await browser.close()

            await status_msg.edit_text("تمت الخطوة الأولى بنجاح! هادي لقطة شاشة من السيرفر:")
            with open(screenshot_path, "rb") as photo:
                await update.message.reply_photo(photo=photo)

            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text(f"حدث خطأ أثناء التنفيذ: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_email))

    print("البوت يعمل الآن على Render...")
    app.run_polling()

if __name__ == "__main__":
    main()
