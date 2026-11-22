import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import base64

# ==========================================
# ⚠️ الإعدادات
# ==========================================
BOT_TOKEN = "8908643988:AAGw_F38zhfb2VD9nX9NQLSvtk5onLHq83c"
ADMIN_ID = 8332387485

# ⚠️ إعدادات GitHub (يجب إنشاء توكن بصلاحية repo)
GITHUB_TOKEN = "ghp_YOUR_GITHUB_TOKEN_HERE" 
GITHUB_USER = "YOUR_GITHUB_USERNAME"
GITHUB_REPO = "YOUR_REPO_NAME"
FILE_PATH = "data.json"

bot = telebot.TeleBot(BOT_TOKEN)
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# دالة تحديث ملف JSON على GitHub
def update_site_data(new_data):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        sha = res.json()['sha']
        content = base64.b64decode(res.json()['content']).decode('utf-8')
        data = json.loads(content)
        
        for key, value in new_data.items():
            data[key] = value
            
        encoded_content = base64.b64encode(json.dumps(data, indent=2).encode('utf-8')).decode('utf-8')
        payload = {"message": "Update via Bot", "content": encoded_content, "sha": sha}
        
        put_res = requests.put(url, headers=headers, json=payload)
        return put_res.status_code == 200
    return False

# لوحة التحكم
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: 
        return
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📝 تغيير العنوان", callback_data="edit_title"))
    markup.row(InlineKeyboardButton("📄 تغيير النص", callback_data="edit_content"))
    markup.row(InlineKeyboardButton("🖼️ تغيير الصورة", callback_data="edit_image"))
    bot.send_message(message.chat.id, "👑 مرحباً بك في لوحة تحكم موقع DARK AURA.\nاختر ما تريد تعديله:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.from_user.id != ADMIN_ID: return
    
    if call.data == "edit_title":
        msg = bot.send_message(call.message.chat.id, "أرسل العنوان الجديد للموقع:")
        bot.register_next_step_handler(msg, process_title)
    elif call.data == "edit_content":
        msg = bot.send_message(call.message.chat.id, "أرسل النص الجديد:")
        bot.register_next_step_handler(msg, process_content)
    elif call.data == "edit_image":
        msg = bot.send_message(call.message.chat.id, "أرسل رابط الصورة الجديدة (URL):")
        bot.register_next_step_handler(msg, process_image)

def process_title(message):
    if update_site_data({"title": message.text}):
        bot.reply_to(message, "✅ تم تحديث العنوان بنجاح!")

def process_content(message):
    if update_site_data({"content": message.text}):
        bot.reply_to(message, "✅ تم تحديث النص بنجاح!")

def process_image(message):
    if update_site_data({"image_url": message.text}):
        bot.reply_to(message, "✅ تم تحديث الصورة بنجاح!")

print("Bot is running... waiting for victims and admin commands.")
bot.infinity_polling()
