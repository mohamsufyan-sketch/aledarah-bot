import os
import random
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

TOKEN = os.getenv("BOT_TOKEN") or "PUT_YOUR_TOKEN_HERE"

TIME_PER_QUESTION = 25

user_data = {}
quiz_sessions = {}

QUIZ_QUESTIONS = [
    {"type":"true_false","question":"التعيين بالمحاباة يعتبر خيانة","answer":True},
    {"type":"true_false","question":"الكفاءة ليست شرطا في التعيينات","answer":False},
    {"type":"multiple_choice","question":"من أهم صفات المسؤول؟","options":["الصدق","الأمانة","الكفاءة","كل ما سبق"],"answer":3},
    {"type":"multiple_choice","question":"أفضل معيار للاختيار الوظيفي هو؟","options":["القرابة","المصلحة","الكفاءة","الشهرة"],"answer":2},
    {"type":"fill_blank","question":"الاختيار الصحيح للمسؤولين يكون على أساس ____","answer":"الكفاءة"},
    {"type":"fill_blank","question":"المحاسبة تضمن ____ في العمل الإداري","answer":"الانضباط"},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 بدء الاختبار", callback_data="start_quiz")]
    ]
    await update.message.reply_text("🤖 أهلا بك في البوت التفاعلي للاختبارات\n\nاضغط بدء الاختبار", reply_markup=InlineKeyboardMarkup(keyboard))

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    questions = random.sample(QUIZ_QUESTIONS, min(5,len(QUIZ_QUESTIONS)))
    
    quiz_sessions[user_id] = {
        "questions": questions,
        "index": 0,
        "score": 0,
        "correct": 0
    }
    await send_question(update, context)

async def send_question(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    session = quiz_sessions[user_id]
    q = session["questions"][session["index"]]

    if q["type"] == "true_false":
        keyboard = [[InlineKeyboardButton("✅ صح", callback_data="ans_true"),
                     InlineKeyboardButton("❌ خطأ", callback_data="ans_false")]]
        text = f"❓ {q['question']}"
        
    elif q["type"] == "multiple_choice":
        keyboard = []
        for i,opt in enumerate(q["options"]):
            keyboard.append([InlineKeyboardButton(opt, callback_data=f"ans_{i}")])
        text = f"❓ {q['question']}"
        
    elif q["type"] == "fill_blank":
        context.user_data["fill_mode"] = True
        text = f"✍️ أكمل الفراغ:\n\n{q['question']}"
        await query.edit_message_text(text)
        return

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    context.application.create_task(timer(context, user_id))

async def timer(context, user_id):
    await asyncio.sleep(TIME_PER_QUESTION)
    session = quiz_sessions.get(user_id)
    if session:
        session["index"] += 1

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = quiz_sessions[user_id]
    q = session["questions"][session["index"]]
    
    is_correct = False
    
    if q["type"] == "true_false":
        is_correct = (query.data == "ans_true") == q["answer"]
    else:
        is_correct = int(query.data.split("_")[1]) == q["answer"]

    await process(update, context, is_correct)

async def fill_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("fill_mode"):
        return
        
    user_id = update.effective_user.id
    session = quiz_sessions[user_id]
    q = session["questions"][session["index"]]
    
    is_correct = update.message.text.strip() == q["answer"]
    context.user_data["fill_mode"] = False
    
    await process(update, context, is_correct)

async def process(update, context, is_correct):
    query = update.callback_query
    user_id = query.from_user.id
    session = quiz_sessions[user_id]

    if is_correct:
        session["score"] += 10
        session["correct"] += 1
        text = "✅ إجابة صحيحة!"
    else:
        text = "❌ إجابة خاطئة!"

    session["index"] += 1
    
    if session["index"] >= len(session["questions"]):
        await show_result(update, context)
    else:
        keyboard = [[InlineKeyboardButton("➡ التالي", callback_data="next")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def next_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    session = quiz_sessions[user_id]

    text = f"""
🏁 انتهى الاختبار

📊 عدد الأسئلة: {len(session['questions'])}
✅ الصحيحة: {session['correct']}
🏆 النقاط: {session['score']}
"""
    keyboard = [[InlineKeyboardButton("🔄 إعادة", callback_data="start_quiz")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="start_quiz"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="ans_"))
    app.add_handler(CallbackQueryHandler(next_q, pattern="next"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fill_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
