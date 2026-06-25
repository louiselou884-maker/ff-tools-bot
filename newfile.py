import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# --- ⚙️ الإعدادات الأساسية ⚙️ ---
TOKEN = "8850139538:AAG-ELvisgyo76u4Z80_DJkVZU5tfHXbJrs"
CHANNEL_USERNAME = "@rexmodstop1"  # معرف قناتك للاشتراك الإجباري في الخاص

# --- 🔒 الروابط المخفية للـ APIs (مستدعاة داخلياً) 🔒 ---
API_INFO = "http://187.127.175.208:5000/Bmw"
API_JWT = "http://shappno-jwt-api-ob54.vercel.app/token"
API_BIO = "http://shappno-long-bio-api-ob54.vercel.app/bio_upload"
API_EAT = "http://shappno-eat-to-access-api-ob54.vercel.app/access_token"
API_ITEM = "http://shappno-profile-item-api-ob54-fhh.vercel.app/item"

# --- 🌐 نصوص ومحتوى البوت بـ 3 لغات 🌐 ---
STRINGS = {
    "ar": {
        "start": """🎮 مرحباً بك في Free Fire Tools Bot

📜 قائمة الأوامر:

🔍 /info UID
جلب معلومات اللاعب الكاملة من سيرفر الهند.

🔑 /jwt UID PASSWORD
استخراج JWT Token و Access Token للحساب.

🎒 /item ACCESS_TOKEN
جلب جميع عناصر الحساب (Profile Items).

🍽 /eat EAT_TOKEN
تحويل EAT Token إلى Access Token.

📝 /bio TEXT | ACCESS_TOKEN
تغيير البايو الطويل للحساب.

🌐 /lang
تغيير لغة البوت (العربية - English - Français).

📊 /ping
عرض سرعة البوت.

👨‍💻 المطور:
@Rexadmin23

📢 القناة:
@rexmodstop1

👥 المجموعة:
@botlouai

━━━━━━━━━━━━━━
🎮 Free Fire Tools Bot
⚡ Fast & Secure System
━━━━━━━━━━━━━━""",
        "force_sub": "⚠️ عذراً عزيزي! يجب عليك الاشتراك في قناة البوت أولاً لاستخدام هذه الخدمة خارج المجموعات.\n\nاشترك هنا: {channel}\nثم اضغط على زر تفعيل البوت 🔄",
        "invalid_uid": "❌ خطأ: يرجى إدخال UID صحيح (أرقام فقط، وطوله بين 5 و 12 رقماً).",
        "loading": "⏳ جاري معالجة طلبك وجلب البيانات...",
        "error": "❌ حدث خطأ أثناء الاتصال بالخادم، يرجى المحاولة لاحقاً.",
        "lang_select": "🌐 الرجاء اختيار لغة البوت المفضلة:"
    },
    "en": {
        "start": "🎮 Welcome to Free Fire Tools Bot\n\n📜 Commands:\n\n🔍 /info UID\n🔑 /jwt UID PASSWORD\n🎒 /item ACCESS_TOKEN\n🍽 /eat EAT_TOKEN\n📝 /bio TEXT | ACCESS_TOKEN\n🌐 /lang\n📊 /ping\n\n👨‍💻 Developer: @Rexadmin23",
        "force_sub": "⚠️ You must subscribe to our channel first.\n\nJoin: {channel}\nThen press Verify 🔄",
        "invalid_uid": "❌ Error: Invalid UID (Digits only, length 5-12).",
        "loading": "⏳ Fetching data, please wait...",
        "error": "❌ Server connection error.",
        "lang_select": "🌐 Please select your language:"
    },
    "fr": {
        "start": "🎮 Bienvenue sur Free Fire Tools Bot\n\n📜 Commandes:\n\n🔍 /info UID\n🔑 /jwt UID PASSWORD\n🎒 /item ACCESS_TOKEN\n🍽 /eat EAT_TOKEN\n📝 /bio TEXT | ACCESS_TOKEN\n🌐 /lang\n📊 /ping\n\n👨‍💻 Dev: @Rexadmin23",
        "force_sub": "⚠️ Abonnez-vous d'abord à la chaîne.\n\nRejoindre: {channel}\nCliquez sur Vérifier 🔄",
        "invalid_uid": "❌ Erreur: UID invalide.",
        "loading": "⏳ Chargement...",
        "error": "❌ Erreur de serveur.",
        "lang_select": "🌐 Choisissez votre langue:"
    }
}

user_languages = {}

def get_lang(user_id):
    return user_languages.get(user_id, "ar")

# --- 🛠️ دالة الفحص الذكي للاشتراك الإجباري (للشات الخاص فقط) 🛠️ ---
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.effective_chat.type != "private":
        return True  # إذا كان في مجموعة، تخطى الفحص فوراً ليعمل البوت بسلاسة
        
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("🔄 تفعيل البوت", callback_data="check_sub")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        STRINGS[lang]["force_sub"].format(channel=CHANNEL_USERNAME),
        reply_markup=reply_markup,
        reply_to_message_id=update.message.message_id
    )
    return False

# --- 🎛️ معالج الأزرار التفاعلية واللغات 🎛️ ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "check_sub":
        try:
            member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                lang = get_lang(user_id)
                await query.edit_message_text(STRINGS[lang]["start"])
            else:
                await context.bot.send_message(chat_id=user_id, text="❌ لم تشترك بالقناة بعد!")
        except Exception:
            await context.bot.send_message(chat_id=user_id, text="❌ حدث خطأ، تأكد من اشتراكك أولاً.")
            
    elif query.data.startswith("set_lang_"):
        chosen_lang = query.data.split("_")[2]
        user_languages[user_id] = chosen_lang
        await query.edit_message_text(STRINGS[chosen_lang]["start"])

# --- 🚀 دوال الأوامر (تتعامل مع الخاص والمجموعات) 🚀 ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not await check_subscription(update, context): return
    await update.message.reply_text(STRINGS[lang]["start"], reply_to_message_id=update.message.message_id)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not await check_subscription(update, context): return

    if len(context.args) != 1:
        await update.message.reply_text("🔍 الاستخدام: `/info UID`", parse_mode="Markdown", reply_to_message_id=update.message.message_id)
        return

    uid = context.args[0]
    if not uid.isdigit() or not (5 <= len(uid) <= 12):
        await update.message.reply_text(STRINGS[lang]["invalid_uid"], reply_to_message_id=update.message.message_id)
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    status_msg = await update.message.reply_text(STRINGS[lang]["loading"], reply_to_message_id=update.message.message_id)
    
    try:
        response = requests.get(f"{API_INFO}?uid={uid}", timeout=20).json()
        basic = response.get("basicInfo", {})
        clan = response.get("clanBasicInfo", {})
        social = response.get("socialInfo", {})
        pet = response.get("petInfo", {})
        credit = response.get("creditScoreInfo", {})

        msg = f"""🎮 معلومات اللاعب

👤 الاسم: {basic.get('nickname', 'غير متوفر')}
🆔 UID: {basic.get('accountId', 'غير متوفر')}
🌍 السيرفر: {basic.get('region', 'غير متوفر')}
⭐ المستوى: {basic.get('level', 'غير متوفر')}
❤️ الإعجابات: {basic.get('liked', 'غير متوفر')}

🏆 الرتبة BR: {basic.get('rank', 'غير متوفر')}
🔥 نقاط BR: {basic.get('rankingPoints', 'غير متوفر')}

🎯 الرتبة CS: {basic.get('csRank', 'غير متوفر')}
⚔️ نقاط CS: {basic.get('csRankingPoints', 'غير متوفر')}

💎 البرايم: {basic.get('primeInfo', {}).get('primeLevel', '0')}
📦 الإصدار: {basic.get('releaseVersion', 'غير متوفر')}

🏰 الكلان: {clan.get('clanName', 'بدون')}
👑 قائد الكلان: {clan.get('captainId', 'غير متوفر')}
👥 الأعضاء: {clan.get('memberNum', '0')}

🐾 الحيوان: {pet.get('id', 'غير متوفر')}
📈 مستوى الحيوان: {pet.get('level', 'غير متوفر')}

🌐 اللغة: {social.get('language', 'غير متوفر')}
✍️ التوقيع:
{social.get('signature', 'لا يوجد')}

💯 Credit Score: {credit.get('creditScore', 'غير متوفر')}"""
        await status_msg.edit_text(msg)
    except Exception:
        await status_msg.edit_text(STRINGS[lang]["error"])

async def jwt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not await check_subscription(update, context): return

    if len(context.args) < 2:
        await update.message.reply_text("🔑 الاستخدام: `/jwt UID PASSWORD`", parse_mode="Markdown", reply_to_message_id=update.message.message_id)
        return
    uid, password = context.args[0], context.args[1]
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    status_msg = await update.message.reply_text(STRINGS[lang]["loading"], reply_to_message_id=update.message.message_id)

    try:
        res = requests.get(f"{API_JWT}?uid={uid}&pass={password}", timeout=20).text
        await status_msg.edit_text(f"🔑 Result:\n\n{res}")
    except Exception:
        await status_msg.edit_text(STRINGS[lang]["error"])

async def item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not await check_subscription(update, context): return

    if len(context.args) != 1:
        await update.message.reply_text("🎒 الاستخدام: `/item ACCESS_TOKEN`", parse_mode="Markdown", reply_to_message_id=update.message.message_id)
        return
    token = context.args[0]
    
    status_msg = await update.message.reply_text(STRINGS[lang]["loading"], reply_to_message_id=update.message.message_id)
    try:
        res = requests.get(f"{API_ITEM}?access={token}", timeout=20).text
        await status_msg.edit_text(f"🎒 Profile Items:\n\n{res}")
    except Exception:
        await status_msg.edit_text(STRINGS[lang]["error"])

async def eat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not await check_subscription(update, context): return

    if len(context.args) != 1:
        await update.message.reply_text("🍽 الاستخدام: `/eat EAT_TOKEN`", parse_mode="Markdown", reply_to_message_id=update.message.message_id)
        return
    eat_token = context.args[0]
    
    status_msg = await update.message.reply_text(STRINGS[lang]["loading"], reply_to_message_id=update.message.message_id)
    try:
        res = requests.get(f"{API_EAT}?eat_token={eat_token}", timeout=20).text
        await status_msg.edit_text(f"🍽 Result:\n\n{res}")
    except Exception:
        await status_msg.edit_text(STRINGS[lang]["error"])

async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not await check_subscription(update, context): return

    text_input = " ".join(context.args)
    if "|" not in text_input:
        await update.message.reply_text("📝 الاستخدام: `/bio TEXT | ACCESS_TOKEN`", parse_mode="Markdown", reply_to_message_id=update.message.message_id)
        return
    
    try:
        bio_text, access_token = text_input.split("|")
        status_msg = await update.message.reply_text(STRINGS[lang]["loading"], reply_to_message_id=update.message.message_id)
        res = requests.get(f"{API_BIO}?bio={bio_text.strip()}&access={access_token.strip()}", timeout=20).text
        await status_msg.edit_text(f"📝 Response:\n\n{res}")
    except Exception:
        await update.message.reply_text(STRINGS[lang]["error"])

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not await check_subscription(update, context): return

    keyboard = [
        [
            InlineKeyboardButton("العربية 🇸🇦", callback_data="set_lang_ar"),
            InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en"),
            InlineKeyboardButton("Français 🇫🇷", callback_data="set_lang_fr")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(STRINGS[lang]["lang_select"], reply_markup=reply_markup, reply_to_message_id=update.message.message_id)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    message = await update.message.reply_text("📊 Checking speed...", reply_to_message_id=update.message.message_id)
    ping_ms = round((time.time() - start_time) * 1000)
    await message.edit_text(f"🚀 Speed: {ping_ms}ms")

# --- 🎬 تهيئة وإقلاع البوت 🎬 ---
def main():
    application = Application.builder().token(TOKEN).build()

    # تسجيل مستمعي الأوامر (تستجيب تلقائياً في المجموعات والخاص)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("jwt", jwt))
    application.add_handler(CommandHandler("item", item))
    application.add_handler(CommandHandler("eat", eat))
    application.add_handler(CommandHandler("bio", bio))
    application.add_handler(CommandHandler("lang", lang_command))
    application.add_handler(CommandHandler("ping", ping))
    
    # مستمع الأزرار التفاعلية
    application.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 البوت شغال الآن بكفاءة عالية في المجموعات والشات الخاص!")
    application.run_polling()

if __name__ == "__main__":
    main()
