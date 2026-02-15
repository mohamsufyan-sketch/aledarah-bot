"""
بوت أسئلة مادة أنشطة الإدارة في الإسلام
نسخة متوافقة مع اسم الملف main.py
"""

import logging
import os
import asyncio
import random
from datetime import datetime
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# استيراد الأسئلة - تم التعديل ليعمل مع main.py
try:
    from questions import *
except ImportError:
    # إذا لم يتم العثور على questions.py، نعرف الأسئلة هنا مباشرة
    print("⚠️ لم يتم العثور على questions.py، سيتم استخدام الأسئلة الافتراضية")
    
    # ==================== أسئلة افتراضية بسيطة ====================
    QUESTIONS = [
        {
            "id": 1,
            "text": "قد يساهم المجتمع في اختلال عمل الجهاز الإداري للدولة من خلال:",
            "options": {"أ": "عدم تفهمه لأهمية توفر الكفاءة", "ب": "فرضه شخصيات غير كفؤة", "ج": "كل ما سبق", "د": "لا شيء"},
            "correct": "ج",
            "explanation": "المجتمع قد يساهم بفرض شخصيات غير كفؤة",
            "lesson": "الدرس 7-8",
            "difficulty": "سهل"
        },
        {
            "id": 2,
            "text": "التعيين في المناصب بالمحاباة والأثرة يعتبر خيانة:",
            "options": {"أ": "لله", "ب": "للناس", "ج": "كل ما سبق", "د": "لا شيء"},
            "correct": "ج",
            "explanation": "المحاباة خيانة لله وللناس",
            "lesson": "الدرس 7-8",
            "difficulty": "سهل"
        }
    ]
    
    def get_all_questions():
        return QUESTIONS
    
    def get_questions_by_lesson(lesson):
        return [q for q in QUESTIONS if q.get('lesson') == lesson]
    
    def get_random_questions(count=5):
        return random.sample(QUESTIONS, min(count, len(QUESTIONS)))
    
    def get_questions_count():
        return len(QUESTIONS)
    
    def get_lessons_list():
        lessons = {}
        for q in QUESTIONS:
            lesson = q.get('lesson', 'عام')
            lessons[lesson] = lessons.get(lesson, 0) + 1
        return lessons

# ==================== إعدادات ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get('BOT_TOKEN', '8550588818:AAHkdtokih3ndkVHYNEEMo__8mKBQsg1tH0')
TIME_LIMIT = 40

# ==================== تخزين البيانات ====================
user_stats = defaultdict(lambda: {
    'total_answered': 0,
    'correct': 0,
    'wrong': 0,
    'streak': 0,
    'best_streak': 0,
    'history': [],
    'join_date': datetime.now().strftime("%Y-%m-%d")
})

question_stats = defaultdict(lambda: {
    'total': 0,
    'correct': 0,
    'wrong': 0,
    'answers': defaultdict(int)
})

# ==================== دوال مساعدة ====================
def format_time(seconds: int) -> str:
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def calculate_percentage(count: int, total: int) -> float:
    return (count / total * 100) if total > 0 else 0

def get_rank(percentage: float) -> str:
    if percentage >= 90:
        return "🏆 ممتاز"
    elif percentage >= 75:
        return "🎯 جيد جداً"
    elif percentage >= 60:
        return "📘 مقبول"
    else:
        return "📚 يحتاج مراجعة"

# ==================== دوال البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.first_name or "صديقي"
    
    text = (
        f"👋 مرحباً {username}!\n\n"
        f"📚 عدد الأسئلة: {get_questions_count()}\n"
        f"⏱️ وقت الإجابة: {TIME_LIMIT} ثانية\n\n"
        f"📌 اختر من القائمة:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار عشوائي", callback_data="quiz_random")],
        [InlineKeyboardButton("📚 اختبار حسب الدرس", callback_data="show_lessons")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")],
        [InlineKeyboardButton("🏆 لوحة الشرف", callback_data="leaderboard")]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lessons = get_lessons_list()
    
    text = "📚 **اختر الدرس:**\n\n"
    keyboard = []
    
    for lesson, count in lessons.items():
        keyboard.append([InlineKeyboardButton(f"{lesson} ({count})", callback_data=f"lesson_{lesson}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = "📌 **القائمة الرئيسية**"
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار عشوائي", callback_data="quiz_random")],
        [InlineKeyboardButton("📚 اختبار حسب الدرس", callback_data="show_lessons")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats")],
        [InlineKeyboardButton("🏆 لوحة الشرف", callback_data="leaderboard")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    stats = user_stats[user_id]
    
    total = stats['total_answered']
    correct = stats['correct']
    wrong = stats['wrong']
    percentage = calculate_percentage(correct, total) if total > 0 else 0
    rank = get_rank(percentage)
    
    text = (
        f"📊 **إحصائياتك:**\n\n"
        f"✅ الصحيحة: {correct}\n"
        f"❌ الخاطئة: {wrong}\n"
        f"📈 النسبة: {percentage:.1f}%\n"
        f"🔥 السلسلة: {stats['streak']}\n"
        f"🏆 أفضل سلسلة: {stats['best_streak']}\n"
        f"⭐ التقييم: {rank}"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    top_users = []
    for user_id, stats in user_stats.items():
        if stats['total_answered'] > 0:
            accuracy = (stats['correct'] / stats['total_answered']) * 100
            top_users.append((stats['correct'], accuracy))
    
    top_users.sort(reverse=True)
    top_users = top_users[:10]
    
    text = "🏆 **لوحة الشرف**\n\n"
    
    if not top_users:
        text += "لا توجد إحصائيات بعد"
    else:
        for i, (correct, accuracy) in enumerate(top_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {correct} صحيحة ({accuracy:.1f}%)\n"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "quiz_random":
        questions = get_random_questions(5)
    else:
        lesson = query.data.replace("lesson_", "")
        questions = get_questions_by_lesson(lesson)
        questions = random.sample(questions, min(5, len(questions)))
    
    context.user_data['quiz'] = {
        'questions': questions,
        'current': 0,
        'score': 0,
        'start_time': datetime.now().isoformat()
    }
    
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz = context.user_data.get('quiz', {})
    
    if not quiz or quiz['current'] >= len(quiz['questions']):
        await end_quiz(update, context)
        return
    
    q = quiz['questions'][quiz['current']]
    current = quiz['current'] + 1
    total = len(quiz['questions'])
    
    keyboard = []
    for opt_key, opt_text in q['options'].items():
        keyboard.append([InlineKeyboardButton(
            f"{opt_key} - {opt_text}",
            callback_data=f"ans_{q['id']}_{opt_key}"
        )])
    
    keyboard.append([InlineKeyboardButton("❌ إنهاء", callback_data="end_quiz")])
    
    text = (
        f"**السؤال {current}/{total}**\n\n"
        f"{q['text']}\n\n"
        f"📚 {q.get('lesson', 'عام')} | {q.get('difficulty', 'متوسط')}"
    )
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "end_quiz":
        await end_quiz(update, context)
        return
    
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
        user_stats[user_id]['streak'] += 1
        user_stats[user_id]['best_streak'] = max(user_stats[user_id]['best_streak'], user_stats[user_id]['streak'])
        feedback = "✅ صحيحة!"
    else:
        user_stats[user_id]['wrong'] += 1
        user_stats[user_id]['streak'] = 0
        feedback = f"❌ خطأ. الإجابة الصحيحة: {q['correct']}"
    
    user_stats[user_id]['total_answered'] += 1
    question_stats[q_id]['total'] += 1
    
    await query.edit_message_text(
        f"{feedback}\n\n➡️ الانتقال للسؤال التالي..."
    )
    
    await asyncio.sleep(1)
    
    quiz['current'] += 1
    await send_question(update, context)

async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    quiz = context.user_data.get('quiz', {})
    score = quiz.get('score', 0)
    total = len(quiz.get('questions', [])) * 10
    percentage = (score / total * 100) if total > 0 else 0
    rank = get_rank(percentage)
    
    user_stats[user_id]['history'].append(f"{score} نقطة")
    
    text = (
        f"🎯 **النتيجة**\n\n"
        f"نقاطك: {score}\n"
        f"النسبة: {percentage:.1f}%\n"
        f"التقييم: {rank}"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار جديد", callback_data="quiz_random")],
        [InlineKeyboardButton("🏠 القائمة", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    
    if 'quiz' in context.user_data:
        del context.user_data['quiz']

# ==================== التشغيل الرئيسي ====================
def main():
    print("╔══════════════════════════════╗")
    print("║   🚀 تشغيل البوت (main.py)  ║")
    print("╚══════════════════════════════╝")
    print(f"✅ عدد الأسئلة: {get_questions_count()}")
    print("✅ البوت يعمل...")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(show_lessons, pattern="^show_lessons$"))
    app.add_handler(CallbackQueryHandler(my_stats, pattern="^my_stats$"))
    app.add_handler(CallbackQueryHandler(leaderboard, pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="^(quiz_random|lesson_)"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(end_quiz, pattern="^end_quiz$"))
    
    app.run_polling()

if __name__ == "__main__":
    main()