from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta

BOT_TOKEN = "8600520128:AAHWqTUajKUpPsJMci-iqu146hTmXO5XBG4"
OWNER_ID = 5170966325
OTHER_USER_ID = 6273003114
import os
TOKEN = os.getenv("8600520128:AAHWqTUajKUpPsJMci-iqu146hTmXO5XBG4")

user_last_time = {}
user_history = {}  
user_medals = {}

# ===== دکمه‌ها =====
def generate_main_keyboard():
    buttons = [
        [InlineKeyboardButton("ثبت حال امروز 🌿", callback_data="mood")],
        [InlineKeyboardButton("ثبت موقعیت‌ها 📌", callback_data="metrics")],
        [InlineKeyboardButton("میانگین هفته 📊", callback_data="average")],
        [InlineKeyboardButton("مدال سبزکی 🌟", callback_data="medals")],
        [InlineKeyboardButton("دل‌نوشته امروز 📝", callback_data="note")]
    ]
    return InlineKeyboardMarkup(buttons)

def generate_mood_buttons():
    values = [5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0]
    buttons, row = [], []
    for i, val in enumerate(values, 1):
        row.append(InlineKeyboardButton(str(val), callback_data=f"mood_{val}"))
        if i % 4 == 0:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("برگشت به منو 🏡", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

def generate_metrics_buttons(metric_name):
    options = ["خوب ✅","متوسط ⚖️","بد ❌"]
    buttons, row = [], []
    for i, opt in enumerate(options,1):
        row.append(InlineKeyboardButton(opt, callback_data=f"{metric_name}_{opt}"))
        if i % 3 == 0:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("برگشت به منو 🏡", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

metrics_list = ["سطح استرس", "سطح تمرکز", "کیفیت درس", "ساعت درس", "کیفیت خواب"]

# ===== استارت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in [OWNER_ID, OTHER_USER_ID]:
        await update.message.reply_text("متاسفم، اجازه استفاده نداری 😔")
        return
    await update.message.reply_text(
        "سلام سبزکی! خوش اومدی 💚\nمن می‌تونم حال روزت و موقعیت‌های مختلفت رو ثبت کنم 😌",
        reply_markup=generate_main_keyboard()
    )

# ===== هندل دکمه =====
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    now = datetime.now()

    if user_id not in [OWNER_ID, OTHER_USER_ID]:
        await query.message.reply_text("دسترسی نداری!")
        return

    if data == "main":
        await query.edit_message_text("منو اصلی 💚", reply_markup=generate_main_keyboard())
        return

    if data == "average":
        history = user_history.get(user_id, [])
        if not history:
            text = "فعلاً هیچ حال روزی ثبت نشده 😔"
        else:
            avg = sum(val for dt, val in history)/len(history)
            text = f"میانگین هفته‌ی تو: {avg:.1f} 💚"
        await query.edit_message_text(text, reply_markup=generate_main_keyboard())
        return

    if data == "medals":
        medals = user_medals.get(user_id, [])
        text = "مدال‌های تو:\n" + ("\n".join(medals) if medals else "هنوز مدالی کسب نکردی 😔")
        await query.edit_message_text(text, reply_markup=generate_main_keyboard())
        return

    # ثبت حال روز
    if data.startswith("mood"):
        if data == "mood":
            await query.edit_message_text("حالت امروزت چنده سبزکی؟ 💚", reply_markup=generate_mood_buttons())
            return
        else:
            val = float(data.split("_")[1])
            last_time = user_last_time.get(user_id)
            if last_time and now - last_time < timedelta(hours=21):
                await query.message.reply_text("چند بار میخوای ثبت کنی سبزکی؟")
                return
            user_last_time[user_id] = now
            if user_id not in user_history:
                user_history[user_id] = []
            user_history[user_id].append((now.date(), val))
            text = "اشکال نداره اگه بعضی وقتا خوب نباشی ولی سبزکی من قوی‌تر از این حرفاست 💚" if val<7.5 else "خوب بودن تو، خوب بودن منم هست، پس همینطوری خوب بمون 🧡"
            await query.edit_message_text(text, reply_markup=generate_main_keyboard())

            # ارسال برای تو
            await context.bot.send_message(chat_id=OWNER_ID, text=f"سبزکی امروز حالش: {val}")
            
            # مدال‌ها
            medals = user_medals.get(user_id, [])
            last3 = [v for d,v in user_history[user_id][-3:]]
            if len(last3)==3 and all(x<7.5 for x in last3) and "🌿 سبزِ پیگیر" not in medals:
                medals.append("🌿 سبزِ پیگیر")
            last10 = [v for d,v in user_history[user_id][-10:]]
            if len(last10)==10 and all(x>=8 for x in last10) and "🏆 سبزِ طلایی" not in medals:
                medals.append("🏆 سبزِ طلایی")
            last14 = [v for d,v in user_history[user_id][-14:]]
            if len(last14)==14 and all(x<=8.5 for x in last14) and "💎 سبزِ ویژه" not in medals:
                medals.append("💎 سبزِ ویژه")
            user_medals[user_id] = medals
            return

    # ثبت موقعیت‌ها
    if data == "metrics":
        metric = metrics_list[0]
        await query.edit_message_text(f"وضعیت {metric}ت چطوره؟", reply_markup=generate_metrics_buttons(metric))
        return

    for metric in metrics_list:
        if data.startswith(metric):
            choice = data.split("_")[1]
            await context.bot.send_message(chat_id=OWNER_ID, text=f"{metric} امروز: {choice}")
            idx = metrics_list.index(metric)
            if idx+1 < len(metrics_list):
                next_metric = metrics_list[idx+1]
                await query.edit_message_text(f"وضعیت {next_metric}ت چطوره؟", reply_markup=generate_metrics_buttons(next_metric))
            else:
                await query.edit_message_text("تمام موقعیت‌ها ثبت شد 💚", reply_markup=generate_main_keyboard())
            return

    # ثبت دل‌نوشته
    if data == "note":
        await query.edit_message_text("دل‌نوشته امروزتو بفرست 💌")
        return

# ===== هندل متن =====
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if user_id in [OWNER_ID, OTHER_USER_ID]:
        # ارسال برای تو
        await context.bot.send_message(chat_id=OWNER_ID, text=f"دل‌نوشته {user_id}: {text}")
        await update.message.reply_text("ثبت شد سبزکی 💌", reply_markup=generate_main_keyboard())

# ===== اپلیکیشن =====
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_button))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

print("ربات سبزکی خوشگل و مدرن روشن شد 💚")
app.run_polling()
