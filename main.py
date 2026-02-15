"""
بوت أسئلة مادة أنشطة الإدارة في الإسلام
نسخة متطورة - واجهة مستخدم احترافية
"""

import logging
import os
import asyncio
import random
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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
    PRIMARY = "🔵"      # أزرق
    SUCCESS = "🟢"      # أخضر
    WARNING = "🟡"      # أصفر
    DANGER = "🔴"       # أحمر
    INFO = "🟣"         # بنفسجي
    GOLD = "🏆"         # ذهبي
    
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

# ==================== جميع الأسئلة ====================
QUESTIONS = [
    # ===== الدرس 7-8 =====
    {
        "id": 1,
        "text": "قد يساهم المجتمع في اختلال عمل الجهاز الإداري للدولة من خلال:",
        "options": {
            "أ": "عدم تفهمه لأهمية توفر الكفاءة",
            "ب": "فرضه شخصيات غير كفؤة في مناصب معينة",
            "ج": "كل (أ) و (ب) صحيح",
            "د": "لا شيء مما سبق"
        },
        "correct": "ج",
        "explanation": "المجتمع قد يساهم بفرض شخصيات غير كفؤة أو بعدم تفهم أهمية الكفاءة",
        "lesson": "الدرس 7-8",
        "difficulty": "متوسط"
    },
    {
        "id": 2,
        "text": "كل التعيينات للمسؤولين المبنية على الميل والمجاملة فقط، وليس على الكفاءة العملية، فيه:",
        "options": {
            "أ": "غير نافذة",
            "ب": "غير مناسبة",
            "ج": "غير جائزة",
            "د": "كل ما سبق"
        },
        "correct": "ج",
        "explanation": "التعيين بالمحاباة غير جائز شرعاً وإدارياً",
        "lesson": "الدرس 7-8",
        "difficulty": "سهل"
    },
    {
        "id": 3,
        "text": "التعيين في المناصب بالمحاباة والأثرة يعتبر خيانة:",
        "options": {
            "أ": "لله سبحانه وتعالى",
            "ب": "للناس وللأمة",
            "ج": "كل ما سبق صحيح",
            "د": "لا شيء مما سبق"
        },
        "correct": "ج",
        "explanation": "المحاباة خيانة لله وللناس وللأمة",
        "lesson": "الدرس 7-8",
        "difficulty": "سهل"
    },
    {
        "id": 4,
        "text": "قول الإمام علي (ع) (من أهل البيوتات الصالحة) يعني أن يكون:",
        "options": {
            "أ": "من أهل الأنساب والأحساب",
            "ب": "ممن ترّبوا على مكارم الأخلاق والقيم الفاضلة",
            "ج": "من الأغنياء",
            "د": "من العلماء فقط"
        },
        "correct": "ب",
        "explanation": "البيوتات الصالحة هي التي تربت على مكارم الأخلاق",
        "lesson": "الدرس 7-8",
        "difficulty": "متوسط"
    },
    {
        "id": 5,
        "text": "من أهم ما يجب ملاحظته عند الرقابة السرية على المسؤول واختباره:",
        "options": {
            "أ": "حسن علاقاته الشخصية",
            "ب": "أداؤه أمانة المسؤولية ورفقه بالناس",
            "ج": "انضباطه في الدوام اليومي",
            "د": "مظهره الخارجي"
        },
        "correct": "ب",
        "explanation": "الأهم هو أداء الأمانة والرفق بالناس",
        "lesson": "الدرس 7-8",
        "difficulty": "متوسط"
    },
    {
        "id": 6,
        "text": "قد يتغير بعض المسؤولين ممن كان ظاهرهم الصالح بسبب:",
        "options": {
            "أ": "إصابته بالغرور والعجب والكبر",
            "ب": "مواجهته واقعا جديدا مغريا",
            "ج": "كل ما سبق صحيح",
            "د": "كثرة الانتقادات"
        },
        "correct": "ج",
        "explanation": "الغرور والواقع الجديد المغرِي قد يغير الإنسان",
        "lesson": "الدرس 7-8",
        "difficulty": "سهل"
    },
    {
        "id": 7,
        "text": "أكثر ما تكون خيانات المسؤولين في:",
        "options": {
            "أ": "المال والإمكانات",
            "ب": "التآمر مع الأعداء",
            "ج": "ظلم الناس",
            "د": "إفشاء الأسرار"
        },
        "correct": "أ",
        "explanation": "المال والإمكانات هي أكثر مجالات الخيانة",
        "lesson": "الدرس 7-8",
        "difficulty": "سهل"
    },
    {
        "id": 8,
        "text": "تراجع اهتمام المسلمين بالزراعة بسبب:",
        "options": {
            "أ": "سياسات الأعداء التي ينفذها الحكام العملاء",
            "б": "الغفلة والتخلف اللذين سادا قرونا من الزمن",
            "ج": "كل ما سبق صحيح",
            "د": "قلة الأراضي"
        },
        "correct": "ج",
        "explanation": "سياسات الأعداء والغفلة سببا تراجع الزراعة",
        "lesson": "الدرس 7-8",
        "difficulty": "متوسط"
    },
    {
        "id": 9,
        "text": "مما يجعل الناس يستفيدون بشكل أكبر من المحاصيل الزراعية:",
        "options": {
            "أ": "الصناعة التحويلية",
            "ب": "إنتاج البذور والمشاتل",
            "ج": "تصنيع الحراثات والحصادات",
            "د": "استيراد المحاصيل"
        },
        "correct": "أ",
        "explanation": "الصناعة التحويلية تزيد القيمة المضافة للمحاصيل",
        "lesson": "الدرس 7-8",
        "difficulty": "صعب"
    },
    {
        "id": 10,
        "text": "إراحة المزارعين والإجمام لهم سيفيد الدولة من حيث:",
        "options": {
            "أ": "اكتساب ثقتهم",
            "ب": "يكونون لها سندا في الظروف الصعبة",
            "ج": "كل ما سبق صحيح",
            "د": "زيادة الضرائب"
        },
        "correct": "ج",
        "explanation": "اكتساب ثقة المزارعين وسندهم يفيد الدولة",
        "lesson": "الدرس 7-8",
        "difficulty": "متوسط"
    }
]

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
        f"  {Style.PRIMARY} عدد الأسئلة: {len(QUESTIONS)}\n"
        f"  {Style.CLOCK} وقت الإجابة: {TIME_LIMIT} ثانية\n"
        f"  {Style.CHART} إحصائيات تفاعلية\n"
        f"  {Style.AWARD} نظام النقاط والمستويات\n\n"
        f"{Style.STAR} **اختر من القائمة أدناه:**"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(f"{Style.PENCIL} اختبار جديد", callback_data="start_quiz"),
            InlineKeyboardButton(f"{Style.CHART} إحصائياتي", callback_data="my_stats")
        ],
        [
            InlineKeyboardButton(f"{Style.BOOK} قائمة الدروس", callback_data="lessons"),
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
        f"  {Style.PRIMARY} إجمالي الأسئلة: {len(QUESTIONS)}\n"
        f"  {Style.CLOCK} مدة الإجابة: {TIME_LIMIT} ثانية\n"
        f"  {Style.USERS} عدد المستخدمين: {len(user_stats)}\n\n"
        f"{Style.GEAR} **الإصدار:** 2.0.0\n"
        f"{Style.CALENDAR} **آخر تحديث:** 15 فبراير 2026\n\n"
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
        f"{Style.FIRE} **السلسلة:** {stats['streak']}\n"
        f"{Style.CROWN} **أفضل سلسلة:** {stats['best_streak']}\n\n"
        f"{rank_emoji} **المستوى:** {rank_text}\n"
        f"{Style.TROPHY} **الرتبة:** {rank}"
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
    lessons_dict = {}
    for q in QUESTIONS:
        lesson = q.get('lesson', 'عام')
        if lesson not in lessons_dict:
            lessons_dict[lesson] = 0
        lessons_dict[lesson] += 1
    
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
            InlineKeyboardButton(f"{Style.PENCIL} اختبار جديد", callback_data="start_quiz"),
            InlineKeyboardButton(f"{Style.CHART} إحصائياتي", callback_data="my_stats")
        ],
        [
            InlineKeyboardButton(f"{Style.BOOK} قائمة الدروس", callback_data="lessons"),
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

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء اختبار جديد"""
    query = update.callback_query
    await query.answer()
    
    # اختيار 10 أسئلة عشوائية
    quiz_questions = random.sample(QUESTIONS, min(10, len(QUESTIONS)))
    
    context.user_data['quiz'] = {
        'questions': quiz_questions,
        'current': 0,
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
    
    # بدء المؤقت
    if 'timer_task' in context.user_data:
        context.user_data['timer_task'].cancel()
    
    loop = asyncio.get_event_loop()
    timer_task = loop.create_task(question_timer(update, context, quiz['current']))
    context.user_data['timer_task'] = timer_task
    
    # إرسال السؤال
    progress_bar = create_progress_bar(current-1, total)
    text = (
        f"{create_header(f'السؤال {current}/{total}')}\n\n"
        f"{Style.THINK} **{q['text']}**\n\n"
        f"{Style.BOOK} **الدرس:** {q.get('lesson', 'عام')}\n"
        f"{Style.CHART} **الصعوبة:** {q.get('difficulty', 'متوسط')}\n\n"
        f"{Style.CLOCK} **الوقت المتبقي:** `{format_time(TIME_LIMIT)}`\n"
        f"{Style.PRIMARY} **التقدم:** {progress_bar}\n"
        f"{Style.SUCCESS} **النقاط:** {quiz['current'] * 10}"
    )
    
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
    """مؤقت السؤال"""
    for remaining in range(TIME_LIMIT, 0, -5):
        await asyncio.sleep(5)
        
        quiz = context.user_data.get('quiz', {})
        if not quiz or quiz['current'] != q_idx:
            return
        
        # تحديث الوقت
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
                f"{Style.SUCCESS} **النقاط:** {q_idx * 10}"
            )
            
            if isinstance(update, Update) and update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=update.callback_query.message.reply_markup,
                    parse_mode="Markdown"
                )
        except:
            pass
    
    # انتهاء الوقت - تسجيل إجابة خاطئة
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
        
        # الانتقال للسؤال التالي
        quiz['current'] += 1
        await send_question(update, context)

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
    answered = quiz.get('current', 0)
    
    stats = user_stats[user_id]
    correct = stats['correct']
    wrong = stats['wrong']
    percentage = calculate_percentage(correct, wrong + correct) if (wrong + correct) > 0 else 0
    
    # حفظ في التاريخ
    date_str = datetime.now().strftime('%Y-%m-%d')
    user_stats[user_id]['history'].append(f"{correct}/{wrong} - {date_str}")
    
    rank, rank_text, rank_emoji = get_rank(percentage)
    
    text = (
        f"{create_header('🎯 نتيجة الاختبار')}\n\n"
        f"{Style.STATS} **الإحصائيات:**\n"
        f"  {Style.SUCCESS} الصحيحة: {correct}\n"
        f"  {Style.DANGER} الخاطئة: {wrong}\n"
        f"  {Style.PRIMARY} النسبة: {percentage:.1f}%\n\n"
        f"{Style.FIRE} **السلسلة الحالية:** {stats['streak']}\n"
        f"{Style.CROWN} **أفضل سلسلة:** {stats['best_streak']}\n\n"
        f"{rank_emoji} **التقييم:** {rank_text}\n"
        f"{rank} **الرتبة:** {rank_text}\n\n"
        f"{Style.CHART} **شريط التقدم:**\n"
        f"{create_progress_bar(correct, total, 20)}"
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
            InlineKeyboardButton(f"{Style.PENCIL} اختبار جديد", callback_data="start_quiz"),
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

# ==================== التشغيل الرئيسي ====================
def main():
    print("╔══════════════════════════════════════╗")
    print("║     🚀 تشغيل البوت المتطور v2.0     ║")
    print("╚══════════════════════════════════════╝")
    print(f"✅ عدد الأسئلة: {len(QUESTIONS)}")
    print(f"⏱️  المهلة: {TIME_LIMIT} ثانية")
    print("✅ نظام الإحصائيات: نشط")
    print("✅ واجهة المستخدم: احترافية")
    print("🚀 البوت يعمل...")
    
    app = Application.builder().token(TOKEN).build()
    
    # أوامر البوت
    app.add_handler(CommandHandler("start", start))
    
    # معالجات الأزرار
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(my_stats, pattern="^my_stats$"))
    app.add_handler(CallbackQueryHandler(lessons, pattern="^lessons$"))
    app.add_handler(CallbackQueryHandler(settings, pattern="^settings$"))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="^start_quiz$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))
    app.add_handler(CallbackQueryHandler(next_question, pattern="^next_question$"))
    app.add_handler(CallbackQueryHandler(end_quiz, pattern="^end_quiz$"))
    
    app.run_polling()

if __name__ == "__main__":
    main()
