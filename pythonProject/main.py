from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import pytz
from datetime import datetime, timedelta

# Replace with your group chat ID
GROUP_CHAT_ID = -1001328920170  # Replace with your actual group chat ID

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Tashkent'))

# Your school's subjects for each day
subjects_by_day = {
    'Monday': ['\n\n🇺🇿 Узбекский язык\n💻 Информатика\n🇷🇺 Русский язык\n🇬🇧 Английский язык\n🏫 НВО'],
    'Tuesday': ['\n\n⚛️ Физика\n🌱 Биология\n📐 Алгебра\n📐 Алгебра\n🧪 Химия'],
    'Wednesday': ['\n\n📐 Алгебра\n👨‍🏫 Воспитание\n📜 История\n🇺🇿 Узбекский язык\n⚽ Физ-ра'],
    'Thursday': ['\n\n⚛️ Физика\n🇺🇿 Узбекский язык\n📖 Литература\n🇬🇧 Английский язык\n🧪 Химия\n⚽ Физ-ра'],
    'Friday': ['\n\n🟨 Классный час\n🗺️ География\n💻 Информатика\n📖 Литература\n📐 Алгебра'],
    'Saturday': ['\n\n📜 История\n⚛️ Физика\n📐 Алгебра\n🌱 Биология\n⚖️ Права']
}





# Day translations to Russian
day_translation = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среду',
    'Thursday': 'Четверг',
    'Friday': 'Пятницу',
    'Saturday': 'Субботу',
    'Sunday': 'Воскресенье'
}


# Sends the subjects for the next day to the group chat
async def send_subjects(chat_id, context):
    tz = pytz.timezone('Asia/Tashkent')
    tomorrow = (datetime.now(tz) + timedelta(days=1)).strftime('%A')
    subjects = subjects_by_day.get(tomorrow, ['No subjects tomorrow!'])

    # Translate day and construct the message
    translated_day = day_translation.get(tomorrow, tomorrow)  # Get Russian day name
    message = f"Предметы на {translated_day} (завтра): {', '.join(subjects)}"
    await context.bot.send_message(chat_id=chat_id, text=message)


# Schedule a message for a specific time
def schedule_message(context, chat_id, schedule_time):
    scheduler.add_job(
        send_subjects,
        trigger=DateTrigger(run_date=schedule_time, timezone=pytz.timezone('Asia/Tashkent')),
        args=[chat_id, context],
    )


# Button handler for scheduling
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'schedule_now':
        await query.message.reply_text("Please choose a time to schedule:")
        keyboard = [
            [InlineKeyboardButton("12:00 PM", callback_data='12:00')],
            [InlineKeyboardButton("02:00 PM", callback_data='14:00')],
            [InlineKeyboardButton("04:00 PM", callback_data='16:00')],
            [InlineKeyboardButton("06:00 PM", callback_data='18:00')],
            [InlineKeyboardButton("08:00 PM", callback_data='20:00')],
            [InlineKeyboardButton("10:00 PM", callback_data='22:00')],
            [InlineKeyboardButton("Schedule for 10 seconds after", callback_data='10_seconds')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Please select a time:", reply_markup=reply_markup)

    elif query.data == '10_seconds':
        schedule_time = datetime.now(pytz.timezone('Asia/Tashkent')) + timedelta(seconds=10)
        chat_id = GROUP_CHAT_ID  # Use group chat ID
        schedule_message(context, chat_id, schedule_time)
        await query.message.reply_text(f"Message scheduled for 10 seconds from now.")

    elif query.data in ['12:00', '14:00', '16:00', '18:00', '20:00', '22:00']:
        chat_id = GROUP_CHAT_ID  # Use group chat ID
        time_str = query.data + ":00"
        schedule_time = datetime.strptime(time_str, "%H:%M:%S").replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            tzinfo=pytz.timezone('Asia/Tashkent')
        )
        schedule_message(context, chat_id, schedule_time)
        await query.message.reply_text(f"Message scheduled for {query.data}.")

    elif query.data == 'send_now':
        chat_id = GROUP_CHAT_ID  # Use group chat ID
        await send_subjects(chat_id, context)
        await query.message.reply_text("Subjects sent to group chat.")


# Command handler for starting the bot
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Schedule the message", callback_data='schedule_now')],
        [InlineKeyboardButton("Send now", callback_data='send_now')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


# Main code to run the bot
if __name__ == "__main__":
    application = ApplicationBuilder().token("7209516474:AAHMX2MtC69RYZbYPljumIDQmm_SIPcrDHs").build()

    # Adding the handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    scheduler.start()
    application.run_polling()
