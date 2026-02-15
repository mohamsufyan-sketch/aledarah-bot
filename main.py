"""
بوت أسئلة مادة أنشطة الإدارة في الإسلام
ملف البوت الرئيسي - منفصل عن الأسئلة
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
from questions import (
    get_all_questions,
    get_questions_by_lesson,
    get_random_questions,
    get_questions_count,
    get_lessons_list,
    get_question_by_id
)

# ==================== إعدادات ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get('BOT_TOKEN', '8550588818:AAHkdtokih3ndkVHYNEEMo__8mKBQsg1tH0')
TIME_LIMIT = 40  # 40 ثانية لكل سؤال

# ==================== أنماط التصميم ====================
class Style:
    # ألوان
    PRIMARY = "🔵"
    SUCCESS = "🟢"
    WARNING = "🟡"
    DANGER = "🔴"
    INFO = "🟣"
    GOLD = "🏆"
    
    # رموز
    CHECK = "✅"
    CROSS = "❌"
    STAR = "⭐"
    CROWN = "👑"
    TROPHY = "🏆"
    MEDAL = "🎖️"
    BOOK = "📚"
    PENCIL = "📝"
    CHART = "📊"
    CLOCK = "⏱️"
    GEAR = "⚙️"
    HOME = "🏠"
    BACK = "🔙"
    NEXT = "➡️"
    PREV = "⬅️"
    MENU = "📋"
    STATS = "📈"
    AWARD = "🎯"
    TARGET = "🎯"
    BRAIN = "🧠"
    THINK = "💭"
    USER = "👤"
    FIRE = "🔥"
    CALENDAR = "📅"
    WAVE = "👋"
    
    # إطارات
    HEADER = "╔══════════════════════════════════╗"
    HEADER_END = "╚══════════════════════════════════╝"
    LINE = "║"
    SEPARATOR = "══════════════════════════════════"

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
def create_progress_bar(current: int, total: int, length: int = 15) -> str:
    """إنشاء شريط تقدم متحرك"""
    filled = int((current / total) * length)
    bar = '█' * filled + '░' * (length - filled)
    percentage = (current / total) * 100
    return f"`{bar}` {percentage:.0f}% ({current}/{total})"

def format_time(seconds: int) -> str:
    """تنسيق الوقت المتبقي"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def calculate_percentage(count: int, total: int) -> float:
    """حساب النسبة المئوية"""
    return (count / total * 100) if total > 0 else 0

def get_rank(percentage: float) -> tuple:
    """الحصول على الرتبة بناءً على النسبة"""
    if percentage >= 90:
        return (Style.CROWN + " " + Style.GOLD, "ممتاز", "🏆")
    elif percentage >= 75:
        return (Style.MEDAL, "جيد جداً", "🥈")
    elif percentage >= 60:
        return (Style.TARGET, "مقبول", "🥉")
    else:
        return (Style.BOOK, "تحتاج للمراجعة", "📚")

def create_header(title: str) -> str:
    """إنشاء رأس الصفحة"""
    return (
        f"{Style.HEADER}\n"
        f"{Style.LINE}  {title.center(38)}  {Style.LINE}\n"
        f"{Style.HEADER_END}"
    )

# ==================== دوال البوت الرئيسية ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الصفحة الرئيسية"""
    user = update.effective_user
    username = user.first_name or "صديقي"
    
    welcome_text = (
        f"{create_header(f'مرحباً {username}')}\n\n"
        f"{Style.WAVE} أهلاً بك في **بوت أنشطة الإدارة**!\n\n"
        f"{Style.BOOK} **معلومات البوت:**\n"
        f"  {Style.PRIMARY} عدد الأسئلة: {get_questions_count()}\n"
        f"  {Style.CLOCK} وقت الإجابة: {TIME_LIMIT} ثانية\n"
        f"  {Style.CHART} إحصائيات تفاعلية\n"
        f"  {Style.AWARD} نظام النقاط والمستويات\n\n"
        f"{Style.STAR} **اختر من القائمة أدناه:**"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(f"{Style.PENCIL} اختبار عشوائي", callback_data="start_quiz_random"),
            InlineKeyboardButton(f"{Style.CHART} إحصائياتي", callback_data="my_stats")
        ],
        [
            InlineKeyboardButton(f"{Style.BOOK} اختبار حسب الدرس", callback_data="lessons"),
            InlineKeyboardButton(f"{Style.TROPHY} لوحة الشرف", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton(f"{Style.GEAR} الإعدادات", callback_data="settings"),
            InlineKeyboardButton(f"{Style.INFO} عن البوت", callback_data="about")
        ]
    ]
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات البوت"""
    query = update.callback_query
    await query.answer()
    
    text = (
        f"{create_header('ℹ️ عن البوت')}\n\n"
        f"{Style.BOOK} **بوت أسئلة مادة أنشطة الإدارة**\n"
        f"{Style.LINE} المستوى الأول - الترم الثاني\n\n"
        f"{Style.STATS} **الإحصائيات:**\n"
        f"  {Style.PRIMARY} إجمالي الأسئلة: {get_questions_count()}\n"
        f"  {Style.CLOCK} مدة الإجابة: {TIME_LIMIT} ثانية\n"
        f"  {Style.USER} عدد المستخدمين: {len(user_stats)}\n\n"
        f"{Style.GEAR} **الإصدار:** 3.0.0\n"
        f"{Style.CALENDAR} **آخر تحديث:** 16 فبراير 2026\n\n"
        f"{Style.WAVE} تم التطوير بواسطة **محمد حسن**"
    )
    
    keyboard = [[InlineKeyboardButton(f"{Style.BACK} العودة", callback_data="main_menu")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

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
    rank, rank_text, rank_emoji = get_rank(percentage)
    
    text = (
        f"{create_header('📊 إحصائياتك الشخصية')}\n\n"
        f"{Style.USER} **المستخدم:** {update.effective_user.first_name}\n"
        f"{Style.CALENDAR} **تاريخ الانضمام:** {stats['join_date']}\n\n"
        f"{Style.CHART} **إحصائيات عامة:**\n"
        f"  {Style.PRIMARY} إجمالي الإجابات: {total}\n"
        f"  {Style.SUCCESS} الصحيحة: {correct}\n"
        f"  {Style.DANGER} الخاطئة: {wrong}\n"
        f"  {Style.CHART} الدقة: {percentage:.1f}%\n\n"
        f"{Style.FIRE} **السلسلة الحالية:** {stats['streak']}\n"
        f"{Style.CROWN} **أفضل سلسلة:** {stats['best_streak']}\n\n"
        f"{rank_emoji} **المستوى:** {rank_text}\n"
        f"{rank} **الرتبة:** {rank_text}"
    )
    
    if stats['history']:
        text += f"\n\n{Style.CLOCK} **آخر 3 اختبارات:**\n"
        for h in stats['history'][-3:]:
            text += f"  {Style.PRIMARY} {h}\n"
    
    keyboard = [[InlineKeyboardButton(f"{Style.BACK} العودة", callback_data="main_menu")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الدروس"""
    query = update.callback_query
    await query.answer()
    
    text = (
        f"{create_header('📚 قائمة الدروس')}\n\n"
        f"{Style.BOOK} اختر الدرس الذي تريد:\n"
    )
    
    # تجميع الدروس
    lessons_dict = get_lessons_list()
    
    keyboard = []
    for lesson, count in lessons_dict.items():
        keyboard.append([InlineKeyboardButton(
            f"{Style.BOOK} {lesson} ({count})",
            callback_data=f"lesson_{lesson}"
        )])
    
    keyboard.append([InlineKeyboardButton(f"{Style.BACK} العودة", callback_data="main_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def lesson_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء اختبار لدرس محدد"""
    query = update.callback_query
    await query.answer()
    
    lesson = query.data.replace("lesson_", "")
    questions = get_questions_by_lesson(lesson)
    
    if not questions:
        await query.edit_message_text("لا توجد أسئلة لهذا الدرس")
        return
    
    # اختيار 5 أسئلة عشوائية من هذا الدرس
    quiz_questions = random.sample(questions, min(5, len(questions)))
    
    context.user_data['quiz'] = {
        'questions': quiz_questions,
        'current': 0,
        'score': 0,
        'answers': [],
        'start_time': datetime.now().isoformat()
    }
    
    await send_question(update, context)

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعدادات المستخدم"""
    query = update.callback_query
    await query.answer()
    
    text = (
        f"{create_header('⚙️ الإعدادات')}\n\n"
        f"{Style.CLOCK} **الوقت الحالي:** {TIME_LIMIT} ثانية\n"
        f"{Style.PRIMARY} **عدد الأسئلة:** 10 لكل اختبار\n\n"
        f"{Style.GEAR} **اختر الإعدادات:**"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(f"{Style.CLOCK} تغيير الوقت", callback_data="set_time"),
            InlineKeyboardButton(f"{Style.CHART} إعادة الإحصائيات", callback_data="reset_stats")
        ],
        [InlineKeyboardButton(f"{Style.BACK} العودة", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة للقائمة الرئيسية"""
    query = update.callback_query
    
    text = (
        f"{create_header('القائمة الرئيسية')}\n\n"
        f"{Style.STAR} مرحباً بعودتك!\n"
        f"{Style.MENU} اختر من القائمة أدناه:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(f"{Style.PENCIL} اختبار عشوائي", callback_data="start_quiz_random"),
            InlineKeyboardButton(f"{Style.CHART} إحصائياتي", callback_data="my_stats")
        ],
        [
            InlineKeyboardButton(f"{Style.BOOK} اختبار حسب الدرس", callback_data="lessons"),
            InlineKeyboardButton(f"{Style.TROPHY} لوحة الشرف", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton(f"{Style.GEAR} الإعدادات", callback_data="settings"),
            InlineKeyboardButton(f"{Style.INFO} عن البوت", callback_data="about")
        ]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def start_quiz_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء اختبار عشوائي"""
    query = update.callback_query
    await query.answer()
    
    # اختيار 10 أسئلة عشوائية من جميع الأسئلة
    quiz_questions = get_random_questions(10)
    
    context.user_data['quiz'] = {
        'questions': quiz_questions,
        'current': 0,
        'score': 0,
        'answers': [],
        'start_time': datetime.now().isoformat()
    }
    
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال السؤال الحالي"""
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
            callback_data=f"answer_{q['id']}_{opt_key}"
        )])
    
    # أزرار التحكم
    control_buttons = [
        InlineKeyboardButton(f"{Style.HOME} إنهاء", callback_data="end_quiz"),
        InlineKeyboardButton(f"{Style.NEXT} تخطي", callback_data="skip_question")
    ]
    keyboard.append(control_buttons)
    
    # إلغاء المؤقت السابق
    if 'timer_task' in context.user_data:
        context.user_data['timer_task'].cancel()
    
    # حفظ وقت بدء السؤال
    context.user_data['question_start_time'] = datetime.now()
    context.user_data['current_question'] = quiz['current']
    
    # إرسال السؤال
    progress_bar = create_progress_bar(current-1, total)
    text = (
        f"{create_header(f'السؤال {current}/{total}')}\n\n"
        f"{Style.THINK} **{q['text']}**\n\n"
        f"{Style.BOOK} **الدرس:** {q.get('lesson', 'عام')}\n"
        f"{Style.CHART} **الصعوبة:** {q.get('difficulty', 'متوسط')}\n\n"
        f"{Style.CLOCK} **الوقت المتبقي:** `{format_time(TIME_LIMIT)}`\n"
        f"{Style.PRIMARY} **التقدم:** {progress_bar}\n"
        f"{Style.SUCCESS} **النقاط الحالية:** {quiz['score']}"
    )
    
    # بدء المؤقت
    loop = asyncio.get_event_loop()
    timer_task = loop.create_task(question_timer(update, context, quiz['current']))
    context.user_data['timer_task'] = timer_task
    
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def question_timer(update: Update, context: ContextTypes.DEFAULT_TYPE, q_idx: int):
    """مؤقت السؤال - يتم تحديثه كل ثانية"""
    try:
        for remaining in range(TIME_LIMIT, 0, -1):
            await asyncio.sleep(1)
            
            quiz = context.user_data.get('quiz', {})
            if not quiz or quiz['current'] != q_idx:
                return
            
            # تحديث الوقت كل 5 ثواني فقط لتقليل الطلبات
            if remaining % 5 == 0 or remaining <= 5:
                try:
                    q = quiz['questions'][q_idx]
                    current = q_idx + 1
                    total = len(quiz['questions'])
                    
                    progress_bar = create_progress_bar(current-1, total)
                    text = (
                        f"{create_header(f'السؤال {current}/{total}')}\n\n"
                        f"{Style.THINK} **{q['text']}**\n\n"
                        f"{Style.BOOK} **الدرس:** {q.get('lesson', 'عام')}\n"
                        f"{Style.CHART} **الصعوبة:** {q.get('difficulty', 'متوسط')}\n\n"
                        f"{Style.CLOCK} **الوقت المتبقي:** `{format_time(remaining)}`\n"
                        f"{Style.PRIMARY} **التقدم:** {progress_bar}\n"
                        f"{Style.SUCCESS} **النقاط الحالية:** {quiz['score']}"
                    )
                    
                    if isinstance(update, Update) and update.callback_query:
                        await update.callback_query.edit_message_text(
                            text,
                            reply_markup=update.callback_query.message.reply_markup,
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    logging.error(f"خطأ في تحديث المؤقت: {e}")
        
        # انتهاء الوقت
        quiz = context.user_data.get('quiz', {})
        if quiz and quiz['current'] == q_idx:
            q = quiz['questions'][q_idx]
            user_id = update.effective_user.id
            
            # تحديث الإحصائيات
            question_stats[q['id']]['total'] += 1
            question_stats[q['id']]['wrong'] += 1
            
            user_stats[user_id]['total_answered'] += 1
            user_stats[user_id]['wrong'] += 1
            user_stats[user_id]['streak'] = 0
            
            # إرسال رسالة انتهاء الوقت
            try:
                await update.callback_query.edit_message_text(
                    f"⏰ **انتهى الوقت!**\n\nالانتقال للسؤال التالي...",
                    parse_mode="Markdown"
                )
                await asyncio.sleep(1)
            except:
                pass
            
            # الانتقال للسؤال التالي
            quiz['current'] += 1
            await send_question(update, context)
            
    except asyncio.CancelledError:
        # تم إلغاء المؤقت
        pass

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الإجابة"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "end_quiz":
        if 'timer_task' in context.user_data:
            context.user_data['timer_task'].cancel()
        await end_quiz(update, context)
        return
    
    if query.data == "skip_question":
        if 'timer_task' in context.user_data:
            context.user_data['timer_task'].cancel()
        
        quiz = context.user_data.get('quiz', {})
        if quiz:
            quiz['current'] += 1
            await send_question(update, context)
        return
    
    # استخراج بيانات الإجابة
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
    
    # حساب الوقت المستغرق
    time_taken = 0
    if 'question_start_time' in context.user_data:
        time_taken = (datetime.now() - context.user_data['question_start_time']).seconds
    
    # إلغاء المؤقت
    if 'timer_task' in context.user_data:
        context.user_data['timer_task'].cancel()
    
    # تحديث الإحصائيات
    question_stats[q_id]['total'] += 1
    question_stats[q_id]['answers'][answer] += 1
    
    is_correct = (answer == q['correct'])
    if is_correct:
        question_stats[q_id]['correct'] += 1
        user_stats[user_id]['correct'] += 1
        user_stats[user_id]['streak'] += 1
        user_stats[user_id]['best_streak'] = max(
            user_stats[user_id]['best_streak'],
            user_stats[user_id]['streak']
        )
        quiz['score'] += 10
    else:
        question_stats[q_id]['wrong'] += 1
        user_stats[user_id]['wrong'] += 1
        user_stats[user_id]['streak'] = 0
    
    user_stats[user_id]['total_answered'] += 1
    
    # حساب توزيع الإجابات
    stats = question_stats[q_id]
    total = stats['total']
    
    result_text = (
        f"{create_header('نتيجة السؤال')}\n\n"
        f"{Style.THINK} **{q['text']}**\n\n"
        f"{Style.CHART} **توزيع الإجابات:**\n"
    )
    
    for opt_key, opt_text in q['options'].items():
        count = stats['answers'][opt_key]
        percent = calculate_percentage(count, total)
        mark = Style.CHECK if opt_key == q['correct'] else Style.CROSS
        result_text += f"{mark} {opt_key}: {percent:.1f}% ({count})\n"
    
    result_text += f"\n{Style.PENCIL} **إجابتك:** {answer}\n"
    result_text += f"{Style.CLOCK} **الوقت:** {time_taken} ثانية\n"
    
    if is_correct:
        result_text += f"{Style.SUCCESS} **✅ إجابة صحيحة!**\n"
        result_text += f"{Style.FIRE} **السلسلة:** {user_stats[user_id]['streak']}\n"
    else:
        result_text += f"{Style.DANGER} **❌ إجابة خاطئة**\n"
        result_text += f"{Style.BOOK} **الإجابة الصحيحة:** {q['correct']}\n"
    
    if 'explanation' in q:
        result_text += f"\n{Style.INFO} **شرح:** {q['explanation']}"
    
    # الانتقال للسؤال التالي
    quiz['current'] += 1
    
    keyboard = [[InlineKeyboardButton(f"{Style.NEXT} السؤال التالي", callback_data="next_question")]]
    await query.edit_message_text(
        result_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الانتقال للسؤال التالي"""
    query = update.callback_query
    await query.answer()
    
    await send_question(update, context)

async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنهاء الاختبار"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    quiz = context.user_data.get('quiz', {})
    total = len(quiz.get('questions', []))
    
    score = quiz.get('score', 0)
    correct = user_stats[user_id]['correct'] - (user_stats[user_id]['correct'] - score//10)  # تقدير تقريبي
    percentage = (score / (total * 10)) * 100 if total > 0 else 0
    
    # حفظ في التاريخ
    date_str = datetime.now().strftime('%Y-%m-%d')
    user_stats[user_id]['history'].append(f"{score} نقطة - {date_str}")
    
    rank, rank_text, rank_emoji = get_rank(percentage)
    
    text = (
        f"{create_header('🎯 نتيجة الاختبار')}\n\n"
        f"{Style.STATS} **الإحصائيات:**\n"
        f"  {Style.SUCCESS} النقاط: {score}\n"
        f"  {Style.PRIMARY} النسبة: {percentage:.1f}%\n\n"
        f"{Style.FIRE} **السلسلة الحالية:** {user_stats[user_id]['streak']}\n"
        f"{Style.CROWN} **أفضل سلسلة:** {user_stats[user_id]['best_streak']}\n\n"
        f"{rank_emoji} **التقييم:** {rank_text}\n"
        f"{rank} **الرتبة:** {rank_text}\n\n"
        f"{Style.CHART} **شريط التقدم:**\n"
        f"{create_progress_bar(score, total*10, 20)}"
    )
    
    if percentage >= 90:
        text += f"\n\n{Style.TROPHY} **ممتاز! استمر بهذا المستوى**"
    elif percentage >= 75:
        text += f"\n\n{Style.MEDAL} **جيد جداً، واصل التقدم**"
    elif percentage >= 60:
        text += f"\n\n{Style.TARGET} **مقبول، يمكنك التحسن**"
    else:
        text += f"\n\n{Style.BOOK} **راجع الدروس وحاول مرة أخرى**"
    
    keyboard = [
        [
            InlineKeyboardButton(f"{Style.PENCIL} اختبار جديد", callback_data="start_quiz_random"),
            InlineKeyboardButton(f"{Style.CHART} إحصائياتي", callback_data="my_stats")
        ],
        [InlineKeyboardButton(f"{Style.HOME} القائمة الرئيسية", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    
    # تنظيف بيانات الجلسة
    if 'quiz' in context.user_data:
        del context.user_data['quiz']

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لوحة الشرف - أفضل المستخدمين"""
    query = update.callback_query
    await query.answer()
    
    # تجميع أفضل المستخدمين
    top_users = []
    for user_id, stats in user_stats.items():
        if stats['total_answered'] > 0:
            accuracy = (stats['correct'] / stats['total_answered']) * 100
            top_users.append((user_id, stats['correct'], accuracy))
    
    # ترتيب تنازلي
    top_users.sort(key=lambda x: x[1], reverse=True)
    top_users = top_users[:10]
    
    text = f"{create_header('🏆 لوحة الشرف')}\n\n"
    
    if not top_users:
        text += "لا توجد إحصائيات بعد"
    else:
        for i, (user_id, correct, accuracy) in enumerate(top_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} المستخدم {i}: {correct} إجابة صحيحة ({accuracy:.1f}%)\n"
    
    keyboard = [[InlineKeyboardButton(f"{Style.BACK} العودة", callback_data="main_menu")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ==================== التشغيل الرئيسي ====================
def main():
    print("╔══════════════════════════════════════╗")
    print("║     🚀 تشغيل البوت المتطور v3.0     ║")
    print("╚══════════════════════════════════════╝")
    print(f"✅ عدد الأسئلة: {get_questions_count()}")
    print(f"⏱️  المهلة: {TIME_LIMIT} ثانية")
    print("✅ نظام الإحصائيات: نشط")
    print("✅ واجهة المستخدم: احترافية")
    print("✅ الأسئلة منفصلة عن التصميم")
    print("🚀 البوت يعمل...")
    
    app = Application.builder().token(TOKEN).build()
    
    # أوامر البوت
    app.add_handler(CommandHandler("start", start))
    
    # معالجات الأزرار
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(my_stats, pattern="^my_stats$"))
    app.add_handler(CallbackQueryHandler(lessons, pattern="^lessons$"))
    app.add_handler(CallbackQueryHandler(lesson_quiz, pattern="^lesson_"))
    app.add_handler(CallbackQueryHandler(settings, pattern="^settings$"))
    app.add_handler(CallbackQueryHandler(leaderboard, pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(start_quiz_random, pattern="^start_quiz_random$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))
    app.add_handler(CallbackQueryHandler(next_question, pattern="^next_question$"))
    app.add_handler(CallbackQueryHandler(end_quiz, pattern="^end_quiz$"))
    
    app.run_polling()

if __name__ == "__main__":
    main()