import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

BOT_TOKEN = '7618565108:AAEBvrce0xRPTKyB4tmW1mG0kvR_acbnX-k'
SUPER_GROUP_ID = -1002649813309

logging.basicConfig(level=logging.INFO)

user_states = {}
user_answers = {}
user_thread_map = {}
autoreset_tasks = {}
total_steps = 4

questions = {
    1: "🧾 Отлично! Расскажи немного о себе.\nЧто ты ищешь? Чем занимаешься? Какие цели ставишь?"
}

def keyboard_next(step):
    return ReplyKeyboardMarkup([
        [KeyboardButton(f"➡️ Дальше (шаг {step}/{total_steps})")],
        [KeyboardButton("🛑 Остановить бота")]
    ], resize_keyboard=True)

def keyboard_cancel():
    return ReplyKeyboardMarkup([[KeyboardButton("❌ Отменить")]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_states[user_id] = 1
    user_answers[user_id] = {}
    if autoreset_tasks.get(user_id):
        autoreset_tasks[user_id].cancel()
    task = asyncio.create_task(auto_reset_form(context, user_id, delay=600))
    autoreset_tasks[user_id] = task
    await update.message.reply_text(
        "👋 Приветствуем в компании *«HR modern»*!\n\n"
        "Чтобы узнать о нас больше, нажмите кнопку ниже 👇",
        reply_markup=keyboard_next(1),
        parse_mode="Markdown"
    )

async def auto_reset_form(context, user_id, delay=600):
    try:
        await asyncio.sleep(delay)
        if user_states.get(user_id) and user_states[user_id] < total_steps:
            await context.bot.send_message(
                chat_id=user_id,
                text="⌛️ Похоже, вы не дошли до конца. Мы сбросили ваш прогресс.\nОтправьте /start, чтобы начать заново."
            )
            user_states.pop(user_id, None)
            user_answers.pop(user_id, None)
    except asyncio.CancelledError:
        pass

async def show_step_content(update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
    user = update.effective_user
    if step == 1:
        await update.message.reply_text(questions[1], reply_markup=ReplyKeyboardRemove())
    elif step == 2:
        await update.message.reply_text(
            "👋 *Привет, будущий партнёр!* 🤝\n\n"
            "*О нас:*\n"
            "Мы — активно расширяющееся рекрутинговое агентство, которое нуждается в молодых и амбициозных партнёрах!\n"
            "Если вы готовы помогать людям находить хорошую работу (и зарабатывать 💸) — поехали!",
            parse_mode="Markdown"
        )
    elif step == 3:
        await update.message.reply_text(
            "💼 *О процессе:*\n\n"
            "Ваша задача — искать и приводить новых курьеров в Я.Еда.\n"
            "⚠️ Обязательно вносите кандидатов в таблицу. Если кандидата не будет в таблице, мы не сможем отследить, ваш ли это кандидат и оплаты не будет!\n\n"
            "💰 Оплата: 600₽ за регистрацию курьера и 5 заказов + 100₽ за каждый следующий (до 100).",
            parse_mode="Markdown"
        )
    elif step == 4:
        await update.message.reply_text(
       "Преимущества работы с нами:\n"
        "1. Гибкий график 🕒. Вы можете работать в удобное для вас время и совмещать эту деятельность с другими проектами, основной работой или учёбой.\n"
        "2. Прозрачная система оплаты 💸. Вы точно будете знать, сколько заработаете за каждого привлечённого курьера, и сможете планировать свой доход. Необходимо будет формировать чеки через приложение \"Мой налог\" для самозанятых, мы будем их оплачивать.\n"
        "3. Поддержка и обучение 🎓. Если у вас нет опыта в рекрутинге, мы поможем вам разобраться и дадим необходимые знания и навыки.\n"
        "4. Возможность заработать 💰. При правильном подходе и активных действиях можно получить хороший дополнительный доход.\n"
        "5. Предоставляем базу для поиска 📊. Ежедневно мы будем предоставлять несколько недавно обновленных резюме с job-сайта в хорошо оплачиваемых регионах.\n"
               "Что мы ожидаем от вас:\n"
        "1. Активность и инициативность ⚡. Нам нужны партнёры, которые готовы самостоятельно искать кандидатов и применять различные методы для привлечения.\n"
        "2. Ответственность ✅. Важно вносить данные по кандидатам в таблицу, чтобы мы могли отслеживать результаты вашей работы.\n"
        "3. Коммуникабельность 🗣️. Умение находить общий язык с людьми и убеждать их — важный навык для успешного рекрутера.\n"
, reply_markup=keyboard_next(4))
    elif step == 5:
        await finish_application(update, context)
        return
    if step < total_steps:
        await update.message.reply_text(
            f"Нажми кнопку *«Дальше»* для продолжения.",
            reply_markup=keyboard_next(step),
            parse_mode="Markdown"
        )

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id
    step = user_states.get(user_id, 1)
    if text.startswith("➡️ Дальше"):
        user_states[user_id] = step + 1
        await show_step_content(update, context, user_states[user_id])
    elif text == "🛑 Остановить бота":
        await update.message.reply_text(
            "❌ Бот остановлен.\nОтправьте /start, чтобы начать заново.",
            reply_markup=ReplyKeyboardRemove()
        )
        user_states.pop(user_id, None)
        user_answers.pop(user_id, None)
    elif text == "❌ Отменить":
        thread_id = user_thread_map.get(user_id)
        if thread_id:
            await context.bot.edit_forum_topic(
                chat_id=SUPER_GROUP_ID,
                message_thread_id=thread_id,
                name=f"❌ Заявка от @{user.username or user.first_name}"
            )
        await update.message.reply_text("🚫 Заявка отменена.", reply_markup=ReplyKeyboardRemove())
    else:
        if step == 1:
            user_answers.setdefault(user_id, {})[step] = text
            await update.message.reply_text("✅ Ответ записан.", reply_markup=keyboard_next(step))

async def finish_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    thread_title = f"✅ Заявка от @{user.username or user.first_name}"
    topic = await context.bot.create_forum_topic(chat_id=SUPER_GROUP_ID, name=thread_title)
    user_thread_map[user_id] = topic.message_thread_id
    answers = user_answers.get(user_id, {})
    lines = [f"📨 Анкета от @{user.username or user.first_name} (ID: {user.id})"]
    for idx, answer in answers.items():
        lines.append(f"\n🧾 Ответ {idx}:\n💬 {answer}")
    await context.bot.send_message(
        chat_id=SUPER_GROUP_ID,
        message_thread_id=topic.message_thread_id,
        text="\n".join(lines)
    )
    task = autoreset_tasks.pop(user_id, None)
    if task:
        task.cancel()
    await update.message.reply_text(
        "Если вы готовы принять вызов и стать частью нашего проекта, ждём вас в нашей команде! 💪! \n"
        "Ожидайте ответа от модератора.",
        reply_markup=keyboard_cancel()
    )

async def handle_link_from_moderator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.is_topic_message:
        return
    thread_id = update.message.message_thread_id
    user_id = next((uid for uid, tid in user_thread_map.items() if tid == thread_id), None)
    if user_id:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📬 Ссылка от модератора:\n👉 {update.message.text}"
        )

async def handle_unstructured_client_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    if user_id in user_thread_map:
        thread_id = user_thread_map[user_id]
        if update.message.text:
            await context.bot.send_message(
                chat_id=SUPER_GROUP_ID,
                message_thread_id=thread_id,
                text=f"👤 {user.first_name}: {update.message.text}"
            )
        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=SUPER_GROUP_ID,
                message_thread_id=thread_id,
                voice=update.message.voice.file_id
            )
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=SUPER_GROUP_ID,
                message_thread_id=thread_id,
                photo=update.message.photo[-1].file_id
            )
        elif update.message.document:
            await context.bot.send_document(
                chat_id=SUPER_GROUP_ID,
                message_thread_id=thread_id,
                document=update.message.document.file_id
            )
        else:
            await update.message.reply_text("✅ Сообщение доставлено модератору.")
    else:
        await update.message.reply_text(
            "🙏 Спасибо! Пожалуйста, завершите беседу или нажмите /start, чтобы начать заново."
        )

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Часто задаваемые вопросы:\n\n"
        "• 💰 Оплата: 600₽ за 5 заказов + 100₽ за каждый следующий (до 100).\n"
        "• 📊 Вносите кандидатов в таблицу.\n"
        "• 🤝 Используйте любые каналы для поиска кандидатов.",
        parse_mode="Markdown"
    )

async def setup_bot_menu(app):
    await app.bot.set_my_commands([
        BotCommand("start", "🔁 Перезапустить бота"),
        BotCommand("faq", "📄 Часто задаваемые вопросы")
    ])

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("faq", faq))
app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, handle_reply))
app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, handle_link_from_moderator))
app.add_handler(MessageHandler(filters.ChatType.PRIVATE, handle_unstructured_client_msg))
app.post_init = setup_bot_menu

app.run_polling()
