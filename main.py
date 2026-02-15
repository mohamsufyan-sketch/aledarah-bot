"""
بوت أسئلة مادة أنشطة الإدارة في الإسلام
نسخة كاملة - 152 سؤال
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
    print(f"✅ تم تحميل {get_questions_count()} سؤال")
except Exception as e:
    print(f"❌ خطأ في تحميل الأسئلة: {e}")
    QUESTIONS = []
    def get_all_questions(): return QUESTIONS
    def get_questions_count(): return 0
    def get_random_questions(count=5): return []

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
    'wrong': 0,
    'history': []
})

# ==================== دوال البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الصفحة الرئيسية"""
    total_q = get_questions_count()
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار (5 أسئلة)", callback_data="quiz_5")],
        [InlineKeyboardButton("📝 اختبار (10 أسئلة)", callback_data="quiz_10")],
        [InlineKeyboardButton("📚 اختبار حسب الدرس", callback_data="lessons")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")]
    ]
    
    await update.message.reply_text(
        f"👋 مرحباً بك في بوت الأسئلة!\n"
        f"📚 إجمالي الأسئلة: {total_q}\n\n"
        f"اختر عدد الأسئلة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الدروس"""
    query = update.callback_query
    await query.answer()
    
    lessons = get_lessons_list()
    keyboard = []
    
    for lesson, count in lessons.items():
        keyboard.append([InlineKeyboardButton(f"{lesson} ({count})", callback_data=f"lesson_{lesson}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="start")])
    
    await query.edit_message_text(
        "📚 اختر الدرس:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء الاختبار"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    
    if data[0] == "quiz":
        # اختبار عشوائي
        count = int(data[1])
        questions = get_random_questions(count)
    else:
        # اختبار حسب الدرس
        lesson = query.data.replace("lesson_", "")
        questions = get_questions_by_lesson(lesson)
        questions = random.sample(questions, min(5, len(questions)))
    
    if not questions:
        await query.edit_message_text("❌ لا توجد أسئلة")
        return
    
    context.user_data['quiz'] = {
        'questions': questions,
        'current': 0,
        'score': 0,
        'total': len(questions)
    }
    
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال السؤال"""
    quiz = context.user_data.get('quiz', {})
    
    if not quiz or quiz['current'] >= quiz['total']:
        await end_quiz(update, context)
        return
    
    q = quiz['questions'][quiz['current']]
    current = quiz['current'] + 1
    total = quiz['total']
    
    # بناء الأزرار
    keyboard = []
    for opt_key, opt_text in q['options'].items():
        keyboard.append([InlineKeyboardButton(
            f"{opt_key} - {opt_text}",
            callback_data=f"ans_{q['id']}_{opt_key}"
        )])
    
    keyboard.append([InlineKeyboardButton("❌ إنهاء", callback_data="end")])
    
    await update.callback_query.edit_message_text(
        f"**السؤال {current}/{total}**\n\n"
        f"{q['text']}\n\n"
        f"📚 {q.get('lesson', 'عام')}",
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
    
    _, q_id, answer = query.data.split('_')
    q_id = int(q_id)
    
    quiz = context.user_data.get('quiz', {})
    if not quiz:
        return
    
    q_idx = quiz['current']
    if q_idx >= quiz['total']:
        return
    
    q = quiz['questions'][q_idx]
    user_id = update.effective_user.id
    
    is_correct = (answer == q['correct'])
    
    if is_correct:
        quiz['score'] += 10
        user_stats[user_id]['correct'] += 1
        feedback = f"✅ **إجابة صحيحة!**\n\n📖 {q.get('explanation', '')}"
    else:
        user_stats[user_id]['wrong'] += 1
        feedback = f"❌ **إجابة خاطئة**\nالإجابة الصحيحة: {q['correct']}\n\n📖 {q.get('explanation', '')}"
    
    user_stats[user_id]['total'] += 1
    quiz['current'] += 1
    
    if quiz['current'] < quiz['total']:
        keyboard = [[InlineKeyboardButton("➡️ السؤال التالي", callback_data="next")]]
        await query.edit_message_text(
            feedback + f"\n\n🏆 نقاطك: {quiz['score']}",
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
    total_q = quiz.get('total', 0)
    max_score = total_q * 10
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    # شريط التقدم
    filled = int((score / max_score) * 10) if max_score > 0 else 0
    progress = '█' * filled + '░' * (10 - filled)
    
    # التقييم
    if percentage >= 90:
        rank = "🏆 ممتاز"
    elif percentage >= 75:
        rank = "🎯 جيد جداً"
    elif percentage >= 60:
        rank = "📘 مقبول"
    else:
        rank = "📚 يحتاج مراجعة"
    
    text = (
        f"🎯 **نتيجة الاختبار**\n\n"
        f"✅ الإجابات الصحيحة: {score//10} من {total_q}\n"
        f"🏆 النقاط: {score} من {max_score}\n"
        f"📊 النسبة: {percentage:.1f}%\n"
        f"⭐ {rank}\n"
        f"📈 [{progress}]"
    )
    
    user_stats[user_id]['history'].append(f"{score} نقطة")
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار جديد", callback_data="quiz_5")],
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
    total = stats['total']
    correct = stats['correct']
    wrong = stats['wrong']
    percentage = (correct / total * 100) if total > 0 else 0
    
    text = (
        f"📊 **إحصائياتك**\n\n"
        f"✅ الصحيحة: {correct}\n"
        f"❌ الخاطئة: {wrong}\n"
        f"📈 الإجمالي: {total}\n"
        f"📊 الدقة: {percentage:.1f}%\n"
    )
    
    if stats['history']:
        text += f"\n🕐 آخر محاولة: {stats['history'][-1]}"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="start")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة للقائمة"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📝 اختبار (5 أسئلة)", callback_data="quiz_5")],
        [InlineKeyboardButton("📝 اختبار (10 أسئلة)", callback_data="quiz_10")],
        [InlineKeyboardButton("📚 اختبار حسب الدرس", callback_data="lessons")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")]
    ]
    
    await query.edit_message_text(
        f"👋 القائمة الرئيسية\n📚 عدد الأسئلة: {get_questions_count()}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== دوال إضافية ====================
def get_lessons_list():
    """جلب قائمة الدروس"""
    try:
        from questions import get_lessons_list as original
        return original()
    except:
        return {"الدرس الأول": 5, "الدرس الثاني": 4}

def get_questions_by_lesson(lesson):
    """جلب أسئلة درس معين"""
    try:
        from questions import get_questions_by_lesson as original
        return original(lesson)
    except:
        return []

def get_random_questions(count):
    """جلب أسئلة عشوائية"""
    try:
        from questions import get_random_questions as original
        return original(count)
    except:
        return []

def get_questions_count():
    """جلب عدد الأسئلة"""
    try:
        from questions import get_questions_count as original
        return original()
    except:
        return 0

# ==================== التشغيل ====================
def main():
    print("╔══════════════════════════════╗")
    print("║   🚀 تشغيل بوت الأسئلة      ║")
    print("╚══════════════════════════════╝")
    print(f"✅ عدد الأسئلة: {get_questions_count()}")
    print("✅ البوت يعمل...")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(show_lessons, pattern="^lessons$"))
    app.add_handler(CallbackQueryHandler(stats, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="^quiz_|^lesson_"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_|^end$"))
    app.add_handler(CallbackQueryHandler(next_question, pattern="^next$"))
    
    app.run_polling()

if __name__ == "__main__":
    main()