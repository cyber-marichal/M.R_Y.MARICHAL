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

# ⚠️ إعدادات GitHub
GITHUB_TOKEN = "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" 
GITHUB_USER = "cyber-marichal"
GITHUB_REPO = "M.R_Y.MARICHAL"
FILE_PATH = "data.json"

bot = telebot.TeleBot(BOT_TOKEN)
headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# دالة تحديث GitHub
def update_site_data(key, value):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        sha = res.json()['sha']
        content = base64.b64decode(res.json()['content']).decode('utf-8')
        data = json.loads(content)
        
        data[key] = value  # تحديث القيمة المطلوبة فقط
        
        encoded_content = base64.b64encode(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        payload = {"message": f"Update {key} via Bot", "content": encoded_content, "sha": sha}
        
        put_res = requests.put(url, headers=headers, json=payload)
        return put_res.status_code == 200
    return False

# القائمة الرئيسية
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = InlineKeyboardMarkup(row_width=2)
    # أزرار التعديل
    markup.add(
        InlineKeyboardButton("📝 العنوان (Title)", callback_data="edit_title"),
        InlineKeyboardButton("📄 النص الفرعي", callback_data="edit_subtitle"),
        InlineKeyboardButton("📜 النص الرئيسي", callback_data="edit_content"),
        InlineKeyboardButton("🔘 نص الزر", callback_data="edit_btn"),
        InlineKeyboardButton("🖼️ رابط الصورة", callback_data="edit_image"),
        InlineKeyboardButton("👤 اسم المطور", callback_data="edit_dev"),
        InlineKeyboardButton("✈️ يوزر تيليجرام", callback_data="edit_tg_user"),
        InlineKeyboardButton("👥 رابط المجموعة", callback_data="edit_tg_group"),
        InlineKeyboardButton("💰 عنوان المحفظة", callback_data="edit_wallet")
    )
    bot.send_message(message.chat.id, "👑 **لوحة التحكم الشاملة**\nاختر العنصر الذي تريد تعديله في الموقع:", reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.from_user.id != ADMIN_ID: return
    
    # خريطة تربط الأزرار بمفاتيح JSON
    keys_map = {
        "edit_title": ("title", "العنوان الرئيسي (Title)"),
        "edit_subtitle": ("subtitle", "النص الفرعي (Subtitle)"),
        "edit_content": ("content", "النص الرئيسي (Content)"),
        "edit_btn": ("btn_text", "نص الزر (Button Text)"),
        "edit_image": ("image_url", "رابط الصورة (Image URL)"),
        "edit_dev": ("developer", "اسم المطور (Developer)"),
        "edit_tg_user": ("telegram_user", "معرف التيليجرام (بدون @)"),
        "edit_tg_group": ("telegram_group", "رابط مجموعة التيليجرام"),
        "edit_wallet": ("wallet", "عنوان المحفظة (Wallet)")
    }
    
    if call.data in keys_map:
        key, prompt = keys_map[call.data]
        msg = bot.send_message(call.message.chat.id, f"أرسل القيمة الجديدة لـ **{prompt}**:", parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_update, key)

def process_update(message, key):
    new_value = message.text.strip()
    bot.reply_to(message, "⏳ جاري التحديث على GitHub...")
    
    if update_site_data(key, new_value):
        bot.send_message(message.chat.id, f"✅ تم تحديث `{key}` بنجاح!\nسيظهر التغيير في الموقع خلال ثوانٍ.", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ فشل التحديث. تأكد من صلاحية التوكن (Token).")

print("Bot is running... Full Control Mode.")
bot.infinity_polling()
