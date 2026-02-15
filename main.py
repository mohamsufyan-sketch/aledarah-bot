"""
بوت أسئلة مادة أنشطة الإدارة في الإسلام
ملف البوت الرئيسي
"""

import logging
import os
import asyncio
import random
from datetime import datetime
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# استيراد الأسئلة من الملف المنفصل
from questions import *

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

# ==================== دوال مساعدة ====================
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
    """الصفحة الرئيسية"""
    user = update.effective_user
    username = user.first_name or "صديقي"
    
    text = (
        f"👋 مرحباً {username} في بوت أنشطة الإدارة!\n\n"
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
    """عرض قائمة الدروس"""
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
    """العودة للقائمة الرئيسية"""
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
    """عرض إحصائيات المستخدم"""
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
    """لوحة الشرف"""
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
    """بدء الاختبار"""
    query = update.callback_query
    await query.answer()
    
    # اختيار 5 أسئلة عشوائية
    if query.data == "quiz_random":
        questions = get_random_questions(5)
    else:
        lesson = query.data.replace("lesson_", "")
        questions = get_questions_by_lesson(lesson)
        if not questions:
            await query.edit_message_text("لا توجد أسئلة لهذا الدرس")
            return
        questions = random.sample(questions, min(5, len(questions)))
    
    if not questions:
        await query.edit_message_text("لا توجد أسئلة متاحة")
        return
    
    context.user_data['quiz'] = {
        'questions': questions,
        'current': 0,
        'score': 0,
        'start_time': datetime.now().isoformat()
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
    
    # بناء أزرار الخيارات
    keyboard = []
    for opt_key, opt_text in q['options'].items():
        keyboard.append([InlineKeyboardButton(
            f"{opt_key} - {opt_text}",
            callback_data=f"ans_{q['id']}_{opt_key}"
        )])
    
    # إضافة زر إنهاء
    keyboard.append([InlineKeyboardButton("❌ إنهاء الاختبار", callback_data="end_quiz")])
    
    text = (
        f"**📝 السؤال {current}/{total}**\n\n"
        f"{q['text']}\n\n"
        f"📚 **الدرس:** {q.get('lesson', 'عام')}\n"
        f"📊 **المستوى:** {q.get('difficulty', 'متوسط')}"
    )
    
    await update.callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الإجابة"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "end_quiz":
        await end_quiz(update, context)
        return
    
    # استخراج بيانات الإجابة
    parts = query.data.split('_')
    if len(parts) != 3:
        return
    
    _, q_id, answer = parts
    q_id = int(q_id)
    
    quiz = context.user_data.get('quiz', {})
    if not quiz:
        return
    
    q_idx = quiz['current']
    if q_idx >= len(quiz['questions']):
        return
    
    q = quiz['questions'][q_idx]
    user_id = update.effective_user.id
    
    # التحقق من الإجابة
    is_correct = (answer == q['correct'])
    
    if is_correct:
        quiz['score'] += 10
        user_stats[user_id]['correct'] += 1
        user_stats[user_id]['streak'] += 1
        if user_stats[user_id]['streak'] > user_stats[user_id]['best_streak']:
            user_stats[user_id]['best_streak'] = user_stats[user_id]['streak']
        feedback = f"✅ **إجابة صحيحة!**\n\n📖 {q.get('explanation', '')}"
    else:
        user_stats[user_id]['wrong'] += 1
        user_stats[user_id]['streak'] = 0
        feedback = f"❌ **إجابة خاطئة**\nالإجابة الصحيحة: {q['correct']}\n\n📖 {q.get('explanation', '')}"
    
    user_stats[user_id]['total_answered'] += 1
    
    # الانتقال للسؤال التالي
    quiz['current'] += 1
    
    # إضافة نقاط
    points_display = f"\n\n🏆 **نقاطك:** {quiz['score']}"
    
    # إذا كان هناك سؤال تالي
    if quiz['current'] < len(quiz['questions']):
        keyboard = [[InlineKeyboardButton("➡️ السؤال التالي", callback_data="next_question")]]
        await query.edit_message_text(
            feedback + points_display,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        # انتهت الأسئلة
        await end_quiz(update, context)

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الانتقال للسؤال التالي"""
    query = update.callback_query
    await query.answer()
    
    await send_question(update, context)

async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنهاء الاختبار وعرض النتيجة"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    quiz = context.user_data.get('quiz', {})
    score = quiz.get('score', 0)
    total_questions = len(quiz.get('questions', []))
    max_score = total_questions * 10
    percentage = (score / max_score * 100) if max_score > 0 else 0
    rank = get_rank(percentage)
    
    # حفظ التاريخ
    if score > 0:
        user_stats[user_id]['history'].append(f"{score} نقطة")
    
    # شريط التقدم
    filled = int((score / max_score) * 10) if max_score > 0 else 0
    progress = '█' * filled + '░' * (10 - filled)
    
    text = (
        f"🎯 **نتيجة الاختبار**\n\n"
        f"✅ **الإجابات الصحيحة:** {score//10} من {total_questions}\n"
        f"🏆 **النقاط:** {score} من {max_score}\n"
        f"📊 **النسبة:** {percentage:.1f}%\n"
        f"⭐ **التقييم:** {rank}\n"
        f"📈 **التقدم:** [{progress}]"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار جديد", callback_data="quiz_random")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    
    # تنظيف بيانات الجلسة
    if 'quiz' in context.user_data:
        del context.user_data['quiz']

# ==================== التشغيل الرئيسي ====================
def main():
    print("╔══════════════════════════════╗")
    print("║   🚀 تشغيل بوت الأسئلة      ║")
    print("╚══════════════════════════════╝")
    print(f"✅ عدد الأسئلة: {get_questions_count()}")
    print("✅ البوت يعمل...")
    print(f"✅ رابط البوت: @Mohamhassansufyan_bot")
    
    app = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(show_lessons, pattern="^show_lessons$"))
    app.add_handler(CallbackQueryHandler(my_stats, pattern="^my_stats$"))
    app.add_handler(CallbackQueryHandler(leaderboard, pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="^(quiz_random|lesson_)"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(next_question, pattern="^next_question$"))
    app.add_handler(CallbackQueryHandler(end_quiz, pattern="^end_quiz$"))
    
    app.run_polling()

if __name__ == "__main__":
    main()