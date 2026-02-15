"""
بوت أسئلة مادة أنشطة الإدارة في الإسلام
نسخة متطابقة مع منصة معهد القرآن
مؤقت 40 ثانية - نافذة أسئلة تفاعلية
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

# ==================== تخزين البيانات ====================
user_stats = defaultdict(lambda: {
    'total_answered': 0,
    'correct': 0,
    'wrong': 0,
    'history': []
})

# إحصائيات الأسئلة (مثل منصة معهد القرآن)
question_stats = defaultdict(lambda: {
    'total': 0,
    'correct': 0,
    'wrong': 0,
    'answers': defaultdict(int)  # توزيع الإجابات
})

# ==================== جميع الأسئلة (قابلة للإضافة) ====================
# يمكنك إضافة أسئلة جديدة هنا بأي وقت
QUESTIONS = [
    # ===== الدرس 7-8 =====
    {
        "id": 1,
        "text": "[1/87] قد يساهم المجتمع في اختلال عمل الجهاز الإداري للدولة من خلال:",
        "options": {
            "أ": "عدم تفهمه لأهمية توفر الكفاءة",
            "ب": "فرضه شخصيات غير كفؤة في مناصب معينة",
            "ج": "كل (أ) و (ب) صحيح",
            "د": "لا شيء مما سبق"
        },
        "correct": "ج",
        "explanation": "المجتمع قد يساهم بفرض شخصيات غير كفؤة أو بعدم تفهم أهمية الكفاءة"
    },
    {
        "id": 2,
        "text": "[2/87] كل التعيينات للمسؤولين المبنية على الميل والمجاملة فقط، وليس على الكفاءة العملية، فيه:",
        "options": {
            "أ": "غير نافذة",
            "ب": "غير مناسبة",
            "ج": "غير جائزة",
            "د": "كل ما سبق"
        },
        "correct": "ج",
        "explanation": "التعيين بالمحاباة غير جائز شرعاً وإدارياً"
    },
    {
        "id": 3,
        "text": "[3/87] التعيين في المناصب بالمحاباة والأثرة يعتبر خيانة:",
        "options": {
            "أ": "لله سبحانه وتعالى",
            "ب": "للناس وللأمة",
            "ج": "كل ما سبق صحيح",
            "د": "لا شيء مما سبق"
        },
        "correct": "ج",
        "explanation": "المحاباة خيانة لله وللناس وللأمة"
    },
    {
        "id": 4,
        "text": "[4/87] قول الإمام علي (ع) (من أهل البيوتات الصالحة) يعني أن يكون:",
        "options": {
            "أ": "من أهل الأنساب والأحساب",
            "ب": "ممن ترّبوا على مكارم الأخلاق والقيم الفاضلة",
            "ج": "من الأغنياء",
            "د": "من العلماء فقط"
        },
        "correct": "ب",
        "explanation": "البيوتات الصالحة هي التي تربت على مكارم الأخلاق"
    },
    {
        "id": 5,
        "text": "[5/87] من أهم ما يجب ملاحظته عند الرقابة السرية على المسؤول واختباره:",
        "options": {
            "أ": "حسن علاقاته الشخصية",
            "ب": "أداؤه أمانة المسؤولية ورفقه بالناس",
            "ج": "انضباطه في الدوام اليومي",
            "د": "مظهره الخارجي"
        },
        "correct": "ب",
        "explanation": "الأهم هو أداء الأمانة والرفق بالناس"
    },
    {
        "id": 6,
        "text": "[6/87] قد يتغير بعض المسؤولين ممن كان ظاهرهم الصالح بسبب:",
        "options": {
            "أ": "إصابته بالغرور والعجب والكبر",
            "ب": "مواجهته واقعا جديدا مغريا",
            "ج": "كل ما سبق صحيح",
            "د": "كثرة الانتقادات"
        },
        "correct": "ج",
        "explanation": "الغرور والواقع الجديد المغرِي قد يغير الإنسان"
    },
    {
        "id": 7,
        "text": "[7/87] أكثر ما تكون خيانات المسؤولين في:",
        "options": {
            "أ": "المال والإمكانات",
            "ب": "التآمر مع الأعداء",
            "ج": "ظلم الناس",
            "د": "إفشاء الأسرار"
        },
        "correct": "أ",
        "explanation": "المال والإمكانات هي أكثر مجالات الخيانة"
    },
    {
        "id": 8,
        "text": "[8/87] تراجع اهتمام المسلمين بالزراعة بسبب:",
        "options": {
            "أ": "سياسات الأعداء التي ينفذها الحكام العملاء",
            "ب": "الغفلة والتخلف اللذين سادا قرونا من الزمن",
            "ج": "كل ما سبق صحيح",
            "د": "قلة الأراضي"
        },
        "correct": "ج",
        "explanation": "سياسات الأعداء والغفلة سببا تراجع الزراعة"
    },
    {
        "id": 9,
        "text": "[9/87] مما يجعل الناس يستفيدون بشكل أكبر من المحاصيل الزراعية:",
        "options": {
            "أ": "الصناعة التحويلية",
            "ب": "إنتاج البذور والمشاتل",
            "ج": "تصنيع الحراثات والحصادات",
            "د": "استيراد المحاصيل"
        },
        "correct": "أ",
        "explanation": "الصناعة التحويلية تزيد القيمة المضافة للمحاصيل"
    },
    {
        "id": 10,
        "text": "[10/87] إراحة المزارعين والإجمام لهم سيفيد الدولة من حيث:",
        "options": {
            "أ": "اكتساب ثقتهم",
            "ب": "يكونون لها سندا في الظروف الصعبة",
            "ج": "كل ما سبق صحيح",
            "د": "زيادة الضرائب"
        },
        "correct": "ج",
        "explanation": "اكتساب ثقة المزارعين وسندهم يفيد الدولة"
    },
    {
        "id": 11,
        "text": "[11/87] أحيانا يشعر المزارع أنه محارب من بعض المسؤولين عندما:",
        "options": {
            "أ": "يفرضون مزيدا من الضرائب على الزراعة",
            "ب": "يكثرون من مضايقاته وفرض الغرامات عليه",
            "ج": "كل ما سبق صحيح",
            "د": "يقدمون له المساعدة"
        },
        "correct": "ج",
        "explanation": "الضرائب والغرامات تجعل المزارع يشعر بالمحاربة"
    },
    {
        "id": 12,
        "text": "[12/87] من مصاديق قول الإمام علي عليه السلام: (فإن العمران محتمل ما حملته):",
        "options": {
            "أ": "البنية الاقتصادية القوية تمثل سندا للبلد في مواجهة التحديات",
            "ب": "عمران المدن بالأعداد الكبيرة من الأبنية",
            "ج": "كثرة السكان",
            "د": "كل ما سبق"
        },
        "correct": "أ",
        "explanation": "العمران القوي يتحمل التحديات"
    },
    {
        "id": 13,
        "text": "[13/87] يعتبر محافظ المحافظة ومدير المديرية من (العمال) الذين ذكرهم الإمام علي (ع).",
        "options": {
            "أ": "صحيح",
            "ب": "خطأ"
        },
        "correct": "أ",
        "explanation": "صحيح، هم من العمال الذين يجب مراقبتهم"
    },
    {
        "id": 14,
        "text": "[14/87] التعيين بالمحاباة والأثرة لا يعطل البناء الحضاري للأمة.",
        "options": {
            "أ": "صحيح",
            "ب": "خطأ"
        },
        "correct": "ب",
        "explanation": "خطأ، المحاباة تعطل البناء الحضاري للأمة"
    },
    {
        "id": 15,
        "text": "[15/87] الرقابة السرية على المسؤولين تحملهم على الرفق بالرعية.",
        "options": {
            "أ": "صحيح",
            "ب": "خطأ"
        },
        "correct": "أ",
        "explanation": "صحيح، الرقابة تدفعهم للرفق"
    },
    {
        "id": 16,
        "text": "[16/87] يستحق الخائن أن يشهر به حتى لا يخدع به الآخرون.",
        "options": {
            "أ": "صحيح",
            "ب": "خطأ"
        },
        "correct": "أ",
        "explanation": "صحيح، التشهير يحذر الآخرين"
    },
    # ===== الدرس 9-10 =====
    {
        "id": 17,
        "text": "[17/87] دور الكتاب (مسؤولي المكاتب) مهم جدا؛ لأنهم:",
        "options": {
            "أ": "يمثلون حلقة الوصل بين المسؤول والمجتمع",
            "ب": "يباشرون إنجاز المعاملات وكثيرا من الترتيبات",
            "ج": "كل ما سبق صحيح",
            "د": "لا شيء مما سبق"
        },
        "correct": "ج",
        "explanation": "الكتاب حلقة وصل ومنفذون للمعاملات"
    },
    {
        "id": 18,
        "text": "[18/87] من أبرز ما عرف عن المكاتب الحكومية في معظم البلدان العربية:",
        "options": {
            "أ": "تأخير معاملات الناس إلى حد كبير",
            "ب": "إنجاز معاملات الناس إلى حد متوسط",
            "ج": "سرعة الإنجاز",
            "د": "العدالة"
        },
        "correct": "أ",
        "explanation": "التأخير من أبرز مشاكل المكاتب الحكومية"
    },
    {
        "id": 19,
        "text": "[19/87] شخص واع وفاهم للعمل، ويجيد الإصدار والإيراد، لكنه يترك حاسوبه في السيارة:",
        "options": {
            "أ": "يجوز استمراره",
            "ب": "يجب استبعاده",
            "ج": "يستثنى",
            "د": "لا بأس"
        },
        "correct": "ب",
        "explanation": "ترك الأسرار في السيارة خرق أمني خطير"
    },
    {
        "id": 20,
        "text": "[20/87] من صفات من (تبطره الكرامة) أنه:",
        "options": {
            "أ": "معجب بنفسه مغرور",
            "ب": "يتصور أنه الأجدر بالمسؤولية",
            "ج": "كل ما سبق صحيح",
            "د": "متواضع"
        },
        "correct": "ج",
        "explanation": "المبتر بالكرامة معجب بنفسه مغرور"
    },
    {
        "id": 21,
        "text": "[21/87] أطلقت العرب على من يتمرد على من يكرمه صفة:",
        "options": {
            "أ": "النمام",
            "ب": "الواشي",
            "ج": "اللئيم",
            "د": "الكريم"
        },
        "correct": "ج",
        "explanation": "اللئيم من يتمرد على من يكرمه"
    },
    {
        "id": 22,
        "text": "[22/87] قول الإمام (لا يضعف عقدا اعتقده لك) يعبر عن:",
        "options": {
            "أ": "الحصافة والإتقان",
            "ب": "الأمانة",
            "ج": "التنظيم",
            "د": "الذكاء"
        },
        "correct": "ب",
        "explanation": "الأمين هو من يفي بالعقود"
    },
    # ===== الدروس التكميلية =====
    {
        "id": 23,
        "text": "[23/87] توجيه الإسلام لأئمة الصلاة أن يصلوا بالناس صلاة أضعفهم بهدف:",
        "options": {
            "أ": "مراعاة ذوي الحاجات والضعفاء",
            "ب": "إرهاق المصلين",
            "ج": "إظهار القوة",
            "د": "لا شيء مما سبق"
        },
        "correct": "أ",
        "explanation": "مراعاة الضعفاء من الإحسان"
    },
    {
        "id": 24,
        "text": "[24/87] الوالي العادل:",
        "options": {
            "أ": "يرضى عنه القريب والبعيد",
            "ب": "لا يرضى عنه أقاربه إذا أقام عليهم الحق",
            "ج": "ينفر منه الأقارب والأباعد",
            "د": "كل ما سبق"
        },
        "correct": "ب",
        "explanation": "العدل قد يغضب الأقارب"
    },
    {
        "id": 25,
        "text": "[25/87] إذا دعانا العدو للصلح فإنه:",
        "options": {
            "أ": "يقبل ما دام الله فيه رضا",
            "ب": "يرفض مطلقاً",
            "ج": "يقبل بلا شروط",
            "د": "يتجاهل"
        },
        "correct": "أ",
        "explanation": "الصلح مقبول إذا كان فيه رضا الله"
    },
    {
        "id": 26,
        "text": "[26/87] من أوثق فرص الشيطان على الإنسان:",
        "options": {
            "أ": "إعجابه بنفسه",
            "ب": "حبه للإطراء والمديح",
            "ج": "كل ما سبق",
            "د": "لا شيء مما سبق"
        },
        "correct": "ج",
        "explanation": "العجب وحب المديح مدخل الشيطان"
    },
    {
        "id": 27,
        "text": "[27/87] (فلا تشخصن همك عنهم) معناه:",
        "options": {
            "أ": "اجعلهم من ضمن أولوياتك",
            "ب": "اهملهم",
            "ج": "تجاهلهم",
            "د": "لا شيء"
        },
        "correct": "أ",
        "explanation": "لا تصرف اهتمامك عنهم"
    },
    {
        "id": 28,
        "text": "[28/87] يجب أن يكون من صفات فريق الرعاية الاجتماعي:",
        "options": {
            "أ": "الخشية لله",
            "ب": "القوة",
            "ج": "الثروة",
            "د": "النسب"
        },
        "correct": "أ",
        "explanation": "الخشية تضمن الإخلاص"
    },
    {
        "id": 29,
        "text": "[29/87] يمكن للمسؤول أن يمنع السائل الغني بغلظة.",
        "options": {
            "أ": "صحيح",
            "ب": "خطأ"
        },
        "correct": "ب",
        "explanation": "التعامل يجب أن يكون بتواضع مع الجميع"
    },
    {
        "id": 30,
        "text": "[30/87] من أسباب التفريط في المسؤولية: مضغ القات ليلا.",
        "options": {
            "أ": "صحيح",
            "ب": "خطأ"
        },
        "correct": "أ",
        "explanation": "يضيع الوقت ويؤخر العمل"
    },
    {
        "id": 31,
        "text": "[31/87] رسول الله أرسل الإمام عليا إلى اليمن مرتين.",
        "options": {
            "أ": "صحيح",
            "ب": "خطأ"
        },
        "correct": "أ",
        "explanation": "نعم، أرسله مرتين"
    },
    {
        "id": 32,
        "text": "[32/87] توجيه الإسلام لأئمة الصلاة أن يصلوا بالناس صلاة أضعفهم لمراعاة ذوي الحاجات والضعفاء.",
        "options": {
            "أ": "صحيح",
            "ب": "خطأ"
        },
        "correct": "أ",
        "explanation": "مراعاة الضعفاء من الإحسان"
    }
]

# ==================== دوال مساعدة ====================
def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """إنشاء شريط تقدم"""
    filled = int((current / total) * length)
    bar = '█' * filled + '░' * (length - filled)
    return f"[{bar}] {current}/{total}"

def format_time(seconds: int) -> str:
    """تنسيق الوقت المتبقي"""
    minutes = seconds // 60
    secs = seconds % 60
    if minutes > 0:
        return f"{minutes}:{secs:02d}"
    return f"00:{secs:02d}"

def calculate_percentage(count: int, total: int) -> float:
    """حساب النسبة المئوية"""
    return (count / total * 100) if total > 0 else 0

# ==================== دوال البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الصفحة الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("📝 بدء الاختبار", callback_data="start_quiz")],
        [InlineKeyboardButton("📊 نتائجي", callback_data="my_results")],
        [InlineKeyboardButton("📈 إحصائيات الأسئلة", callback_data="global_stats")],
        [InlineKeyboardButton("ℹ️ عن البوت", callback_data="about")]
    ]
    
    await update.message.reply_text(
        "**📚 بوت أسئلة أنشطة الإدارة في الإسلام**\n"
        "المستوى الأول - الترم الثاني\n\n"
        f"📊 إجمالي الأسئلة: {len(QUESTIONS)}\n"
        f"⏱️ مدة الإجابة: {TIME_LIMIT} ثانية\n"
        "📈 يظهر توزيع الإجابات بعد كل سؤال\n\n"
        "_اختر من القائمة:_",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات البوت"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "**ℹ️ عن البوت**\n\n"
        "📚 بوت أسئلة مادة أنشطة الإدارة في الإسلام\n"
        "📌 المستوى الأول - الترم الثاني\n"
        f"📊 يحتوي على {len(QUESTIONS)} سؤال\n"
        f"⏱️ مهلة الإجابة: {TIME_LIMIT} ثانية\n"
        "📈 يعرض توزيع إجابات المستخدمين\n\n"
        "🔄 **قابل للتوسع:** يمكن إضافة أسئلة جديدة بسهولة"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def my_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض نتائج المستخدم"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    stats = user_stats[user_id]
    total = stats['total_answered']
    correct = stats['correct']
    wrong = stats['wrong']
    percentage = calculate_percentage(correct, total) if total > 0 else 0
    
    text = (
        "**📊 نتائجك الشخصية**\n\n"
        f"📝 الإجابات الكلية: {total}\n"
        f"✅ الصحيحة: {correct}\n"
        f"❌ الخاطئة: {wrong}\n"
        f"📈 النسبة: {percentage:.1f}%\n"
    )
    
    if stats['history']:
        text += f"\n🕐 آخر اختبار: {stats['history'][-1]}"
    
    keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def global_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات عامة للأسئلة"""
    query = update.callback_query
    
    total_answers = sum(q_stats['total'] for q_stats in question_stats.values())
    total_correct = sum(q_stats['correct'] for q_stats in question_stats.values())
    
    text = (
        "**📈 إحصائيات الأسئلة**\n\n"
        f"📊 إجمالي الإجابات: {total_answers}\n"
        f"✅ الإجابات الصحيحة: {total_correct}\n"
        f"❌ الإجابات الخاطئة: {total_answers - total_correct}\n"
        f"📊 دقة المستخدمين: {calculate_percentage(total_correct, total_answers):.1f}%\n\n"
        "_اختر سؤالاً لرؤية توزيع إجاباته_"
    )
    
    # إضافة أزرار لأشهر الأسئلة
    keyboard = []
    for i in range(min(5, len(QUESTIONS))):
        q = QUESTIONS[i]
        keyboard.append([InlineKeyboardButton(f"سؤال {q['id']}", callback_data=f"q_stats_{q['id']}")])
    
    keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="main_menu")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def question_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات سؤال محدد"""
    query = update.callback_query
    q_id = int(query.data.replace("q_stats_", ""))
    
    q = next((q for q in QUESTIONS if q['id'] == q_id), None)
    if not q:
        return
    
    stats = question_stats[q_id]
    total = stats['total']
    
    text = f"**📊 إحصائيات {q['text']}**\n\n"
    
    if total > 0:
        correct_percent = calculate_percentage(stats['correct'], total)
        text += f"✅ الصحيحة: {stats['correct']} ({correct_percent:.1f}%)\n"
        text += f"❌ الخاطئة: {stats['wrong']} ({100 - correct_percent:.1f}%)\n\n"
        text += "**📊 توزيع الإجابات:**\n"
        
        for opt, count in stats['answers'].items():
            percent = calculate_percentage(count, total)
            text += f"{opt}: {count} ({percent:.1f}%)\n"
    else:
        text += "لم يجب أحد على هذا السؤال بعد"
    
    keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="global_stats")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة للقائمة الرئيسية"""
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton("📝 بدء الاختبار", callback_data="start_quiz")],
        [InlineKeyboardButton("📊 نتائجي", callback_data="my_results")],
        [InlineKeyboardButton("📈 إحصائيات الأسئلة", callback_data="global_stats")],
        [InlineKeyboardButton("ℹ️ عن البوت", callback_data="about")]
    ]
    
    await query.edit_message_text(
        "**📚 بوت أسئلة أنشطة الإدارة في الإسلام**\n\n"
        "_اختر من القائمة:_",
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
    user_id = update.effective_user.id
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
    
    keyboard.append([InlineKeyboardButton("⏹️ إنهاء", callback_data="end_quiz")])
    
    # بدء المؤقت
    if 'timer_task' in context.user_data:
        context.user_data['timer_task'].cancel()
    
    loop = asyncio.get_event_loop()
    timer_task = loop.create_task(question_timer(update, context, quiz['current']))
    context.user_data['timer_task'] = timer_task
    
    # إرسال السؤال
    text = (
        f"**السؤال [{current}/{total}]**\n\n"
        f"{q['text']}\n\n"
        f"⏱️ الوقت المتبقي: {format_time(TIME_LIMIT)}\n"
        f"📊 التقدم: {create_progress_bar(current-1, total)}"
    )
    
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
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
            
            text = (
                f"**السؤال [{current}/{total}]**\n\n"
                f"{q['text']}\n\n"
                f"⏱️ الوقت المتبقي: {format_time(remaining)}\n"
                f"📊 التقدم: {create_progress_bar(current-1, total)}"
            )
            
            if isinstance(update, Update) and update.callback_query:
                await update.callback_query.edit_message_text(
                    text, reply_markup=update.callback_query.message.reply_markup, parse_mode="Markdown"
                )
        except:
            pass
    
    # انتهاء الوقت
    quiz = context.user_data.get('quiz', {})
    if quiz and quiz['current'] == q_idx:
        # تسجيل إجابة خاطئة لانتهاء الوقت
        q = quiz['questions'][q_idx]
        user_id = update.effective_user.id
        
        # تحديث الإحصائيات
        question_stats[q['id']]['total'] += 1
        question_stats[q['id']]['wrong'] += 1
        
        user_stats[user_id]['total_answered'] += 1
        user_stats[user_id]['wrong'] += 1
        
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
    else:
        question_stats[q_id]['wrong'] += 1
        user_stats[user_id]['wrong'] += 1
    
    user_stats[user_id]['total_answered'] += 1
    
    # حساب توزيع الإجابات
    stats = question_stats[q_id]
    total = stats['total']
    
    result_text = (
        f"**{q['text']}**\n\n"
        "**📊 نتائج الإجابات:**\n"
    )
    
    for opt_key, opt_text in q['options'].items():
        count = stats['answers'][opt_key]
        percent = calculate_percentage(count, total)
        mark = "✅" if opt_key == q['correct'] else "❌"
        result_text += f"{mark} {opt_key}: {percent:.1f}% ({count})\n"
    
    result_text += f"\n**إجابتك:** {answer}\n"
    result_text += "✅ صحيحة" if is_correct else "❌ خاطئة"
    
    if 'explanation' in q:
        result_text += f"\n\n📖 {q['explanation']}"
    
    # الانتقال للسؤال التالي
    quiz['current'] += 1
    
    keyboard = [[InlineKeyboardButton("➡️ التالي", callback_data="next_question")]]
    await query.edit_message_text(
        result_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
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
    
    # حساب النتائج من إحصائيات المستخدم
    stats = user_stats[user_id]
    correct = stats['correct']
    wrong = stats['wrong']
    percentage = calculate_percentage(correct, wrong + correct) if (wrong + correct) > 0 else 0
    
    # حفظ في التاريخ
    user_stats[user_id]['history'].append(f"{correct}/{wrong} - {datetime.now().strftime('%Y-%m-%d')}")
    
    text = (
        "**🎯 انتهى الاختبار!**\n\n"
        f"✅ الصحيحة: {correct}\n"
        f"❌ الخاطئة: {wrong}\n"
        f"📊 النسبة: {percentage:.1f}%\n\n"
    )
    
    if percentage >= 90:
        text += "🏆 مستوى متقدم - ممتاز!"
    elif percentage >= 75:
        text += "🎯 مستوى جيد جداً"
    elif percentage >= 60:
        text += "📘 مستوى مقبول"
    else:
        text += "📚 تحتاج للمراجعة"
    
    keyboard = [
        [InlineKeyboardButton("🔄 اختبار جديد", callback_data="start_quiz")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

# ==================== التشغيل الرئيسي ====================
def main():
    print("╔══════════════════════════════╗")
    print("║   🚀 تشغيل البوت المتطور     ║")
    print("╚══════════════════════════════╝")
    print(f"✅ عدد الأسئلة: {len(QUESTIONS)}")
    print(f"⏱️  المهلة: {TIME_LIMIT} ثانية")
    print("✅ نظام الإحصائيات: نشط")
    print("🚀 البوت يعمل...")
    
    app = Application.builder().token(TOKEN).build()
    
    # أوامر البوت
    app.add_handler(CommandHandler("start", start))
    
    # معالجات الأزرار
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(my_results, pattern="^my_results$"))
    app.add_handler(CallbackQueryHandler(global_stats, pattern="^global_stats$"))
    app.add_handler(CallbackQueryHandler(question_stats, pattern="^q_stats_"))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="^start_quiz$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))
    app.add_handler(CallbackQueryHandler(next_question, pattern="^next_question$"))
    app.add_handler(CallbackQueryHandler(end_quiz, pattern="^end_quiz$"))
    
    app.run_polling()

if __name__ == "__main__":
    main()
