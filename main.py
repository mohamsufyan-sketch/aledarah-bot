"""
بوت أسئلة مادة أنشطة الإدارة في الإسلام
نسخة مبسطة ومضمونة 100%
"""

import logging
import os
import random
from datetime import datetime
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# استيراد الأسئلة
try:
    from questions import *
except:
    # إذا لم يتم العثور على questions.py، نعرف أسئلة بسيطة هنا
    QUESTIONS = [
        {
            "id": 1,
            "text": "من أهم مصاديق القسط في الإسلام هو:",
            "options": {"أ": "الظلم", "ب": "العدل", "ج": "التساهل", "د": "التشدد"},
            "correct": "ب",
            "explanation": "القسط يعني العدل",
            "lesson": "الدرس الأول"
        }
    ]
    def get_all_questions(): return QUESTIONS
    def get_questions_count(): return len(QUESTIONS)
    def get_random_questions(count=5): return random.sample(QUESTIONS, min(count, len(QUESTIONS)))

# ==================== إعدادات ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8550588818:AAHkdtokih3ndkVHYNEEMo__8mKBQsg1tH0"

# ==================== تخزين البيانات ====================
user_stats = defaultdict(lambda: {
    'total': 0,
    'correct': 0,
    'wrong': 0
})

# ==================== دوال البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الصفحة الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("📝 اختبار عشوائي", callback_data="quiz")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")]
    ]
    
    await update.message.reply_text(
        f"👋 مرحباً بك في بوت الأسئلة!\n"
        f"📚 عدد الأسئلة: {get_questions_count()}\n\n"
        f"اختر من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء الاختبار"""
    query = update.callback_query
    await query.answer()
    
    # اختيار 3 أسئلة عشوائية
    questions = get_random_questions(3)
    context.user_data['quiz'] = {
        'questions': questions,
        'current': 0,
        'score': 0
    }
    
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال السؤال"""
    quiz = context.user_data.get('quiz', {})
    
    if not quiz or quiz['current'] >= len(quiz['questions']):
        await end_quiz(update, context)
        return
    
    q = quiz['questions'][quiz['current']]
    current = quiz['current'] + 1
    total = len(quiz['questions'])
    
    # بناء الأزرار
    keyboard = []
    for opt_key, opt_text in q['options'].items():
        keyboard.append([InlineKeyboardButton(
            f"{opt_key} - {opt_text}",
            callback_data=f"ans_{q['id']}_{opt_key}"
        )])
    
    keyboard.append([InlineKeyboardButton("❌ إنهاء", callback_data="end")])
    
    await update.callback_query.edit_message_text(
        f"**السؤال {current}/{total}**\n\n{q['text']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الإجابة"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "end":
        await end_quiz(update, context)
        return
    
    # استخراج الإجابة
    _, q_id, answer = query.data.split('_')
    q_id = int(q_id)
    
    quiz = context.user_data.get('quiz', {})
    if not quiz:
        return
    
    q_idx = quiz['current']
    if q_idx >= len(quiz['questions']):
        return
    
    q = quiz['questions'][q_idx]
    user_id = update.effective_user.id
    
    is_correct = (answer == q['correct'])
    
    if is_correct:
        quiz['score'] += 10
        user_stats[user_id]['correct'] += 1
        feedback = f"✅ صحيحة!\n\n📖 {q.get('explanation', '')}"
    else:
        user_stats[user_id]['wrong'] += 1
        feedback = f"❌ خطأ\nالإجابة الصحيحة: {q['correct']}\n\n📖 {q.get('explanation', '')}"
    
    user_stats[user_id]['total'] += 1
    
    # السؤال التالي
    quiz['current'] += 1
    
    if quiz['current'] < len(quiz['questions']):
        keyboard = [[InlineKeyboardButton("➡️ التالي", callback_data="next")]]
        await query.edit_message_text(
            feedback,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await end_quiz(update, context)

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """السؤال التالي"""
    query = update.callback_query
    await query.answer()
    await send_question(update, context)

async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنهاء الاختبار"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    quiz = context.user_data.get('quiz', {})
    score = quiz.get('score', 0)
    total = len(quiz.get('questions', []))
    
    percentage = (score / (total * 10)) * 100 if total > 0 else 0
    
    text = (
        f"🎯 **النتيجة**\n\n"
        f"✅ النقاط: {score}\n"
        f"📊 النسبة: {percentage:.1f}%\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار جديد", callback_data="quiz")],
        [InlineKeyboardButton("🏠 القائمة", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
    if 'quiz' in context.user_data:
        del context.user_data['quiz']

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإحصائيات"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    stats = user_stats[user_id]
    
    text = (
        f"📊 **إحصائياتك**\n\n"
        f"✅ الصحيحة: {stats['correct']}\n"
        f"❌ الخاطئة: {stats['wrong']}\n"
        f"📈 المجموع: {stats['total']}"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="start")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة للقائمة"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار عشوائي", callback_data="quiz")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")]
    ]
    
    await query.edit_message_text(
        f"👋 القائمة الرئيسية\n📚 عدد الأسئلة: {get_questions_count()}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== تشغيل البوت ====================
def main():
    print("🚀 تشغيل البوت...")
    print(f"✅ عدد الأسئلة: {get_questions_count()}")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(quiz, pattern="^quiz$"))
    app.add_handler(CallbackQueryHandler(stats, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(next_question, pattern="^next$"))
    app.add_handler(CallbackQueryHandler(end_quiz, pattern="^end$"))
    
    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()