"""
بوت أسئلة مادة أنشطة الإدارة في الإسلام
المستوى الأول - الترم الثاني
"""

import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ==================== إعدادات ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# التوكن - هنضيفه كمتغير بيئة
TOKEN = os.environ.get('BOT_TOKEN', '8550588818:AAHkdtokih3ndkVHYNEEMo__8mKBQsg1tH0')

# ==================== بنك الأسئلة (الدرس 7-8) ====================
MCQ_7_8 = [
    {
        "question": "1- قد يساهم المجتمع في اختلال عمل الجهاز الإداري للدولة من خلال:",
        "options": ["أ- عدم تفهمه لأهمية توفر الكفاءة", "ب- فرضه شخصيات غير كفؤة في مناصب معينة", "ج- كل (أ) و (ب) صحيح"],
        "correct": "ج"
    },
    {
        "question": "2- كل التعيينات للمسؤولين المبنية على الميل والمجاملة فقط، وليس على الكفاءة العملية، فيه:",
        "options": ["أ- غير نافذة", "ب- غير مناسبة", "ج- غير جائزة"],
        "correct": "ج"
    },
    {
        "question": "3- التعيين في المناصب بالمحاباة والأثرة يعتبر خيانة:",
        "options": ["أ- لله سبحانه وتعالى", "ب- للناس وللأمة", "ج- كل ما سبق صحيح"],
        "correct": "ج"
    },
    {
        "question": "4- قول الإمام علي (ع) (من أهل البيوتات الصالحة) يعني أن يكون:",
        "options": ["أ- من أهل الأنساب والأحساب", "ب- ممن ترّبوا على مكارم الأخلاق والقيم الفاضلة", "ج- كل ما سبق غير صحيح"],
        "correct": "ب"
    },
    {
        "question": "5- من أهم ما يجب ملاحظته عند الرقابة السرية على المسؤول واختباره:",
        "options": ["أ- حسن علاقاته الشخصية", "ب- أداؤه أمانة المسؤولية ورفقه بالناس", "ج- انضباطه في الدوام اليومي"],
        "correct": "ب"
    },
    {
        "question": "6- قد يتغير بعض المسؤولين ممن كان ظاهرهم الصالح بسبب:",
        "options": ["أ- إصابته بالغرور والعجب والكبر", "ب- مواجهته واقعا جديدا مغريا", "ج- كل ما سبق صحيح"],
        "correct": "ج"
    },
    {
        "question": "7- أكثر ما تكون خيانات المسؤولين في:",
        "options": ["أ- المال والإمكانات", "ب- التآمر مع الأعداء", "ج- ظلم الناس"],
        "correct": "أ"
    },
    {
        "question": "8- تراجع اهتمام المسلمين بالزراعة بسبب:",
        "options": ["أ- سياسات الأعداء التي ينفذها الحكام العملاء", "ب- الغفلة والتخلف اللذين سادا قرونا من الزمن", "ج- كل ما سبق صحيح"],
        "correct": "ج"
    },
    {
        "question": "9- مما يجعل الناس يستفيدون بشكل أكبر من المحاصيل الزراعية:",
        "options": ["أ- الصناعة التحويلية", "ب- إنتاج البذور والمشاتل", "ج- تصنيع الحراثات والحصادات"],
        "correct": "أ"
    },
    {
        "question": "10- إراحة المزارعين والإجمام لهم سيفيد الدولة من حيث:",
        "options": ["أ- اكتساب ثقتهم", "ب- يكونون لها سندا في الظروف الصعبة", "ج- كل ما سبق صحيح"],
        "correct": "ج"
    },
    {
        "question": "11- أحيانا يشعر المزارع أنه محارب من بعض المسؤولين عندما:",
        "options": ["أ- يفرضون مزيدا من الضرائب على بعض متطلبات الزراعة", "ب- يُكثرون من مضايقاته وفرض الغرامات عليه", "ج- كل ما سبق صحيح"],
        "correct": "ج"
    },
    {
        "question": "12- من مصاديق قول الإمام علي عليه السلام: (فإن العمران مُحتمل ما حملته):",
        "options": ["أ- البنية الاقتصادية القوية تمثل سندا كبير للبلد في مواجهة التحديات الكبيرة", "ب- عمران المدن بالأعداد الكبيرة من الأبنية لتحتمل قصف العدوان", "ج- كل ما سبق غير صحيح"],
        "correct": "أ"
    }
]

TF_7_8 = [
    {
        "question": "1- يُعتبر محافظ المحافظة ومدير المديرية من (العمال) الذين ذكرهم الإمام علي (ع) في قوله (ثم انظر في أمور عمالك).",
        "correct": "صحيح"
    },
    {
        "question": "2- التعيين للمسؤولين، بناءً على المحاباة والأثرة جريمة كبيرة، ولكنه لا يُعطل البناء الحضاري للأمة.",
        "correct": "خطأ"
    },
    {
        "question": "3- يُفهم من كلام الإمام علي (ع) أنه يجب اختبار المسؤولين في كفاءتهم بعد تعيينهم في مسؤولياتهم.",
        "correct": "خطأ"
    },
    {
        "question": "4- الرقابة السرية على المسؤولين تحملهم على الرفق بالرعية.",
        "correct": "صحيح"
    },
    {
        "question": "5- يستحق الخائن أن يشهر به حتى لا يُخدع به الآخرون فيعتمدوا عليه في عمل جديد.",
        "correct": "صحيح"
    },
    {
        "question": "6- نجحت كثير من الشعوب والأمم من غير العرب والمسلمين في النهضة الزراعية؛ لأنهم اعتبروها مجرد مورد من موارد الاقتصاد فقط.",
        "correct": "خطأ"
    },
    {
        "question": "7- ذكر السيد القائد في الدرس أن من الحلول لضبط كلفة المنتج الزراعي: الاستفادة من تجارب بلدان العالم التي تنتج بكلفة أقل.",
        "correct": "صحيح"
    },
    {
        "question": "8- كان التعليم الزراعي في المراحل الماضية متوسطا لا يرقى إلى المستوى اللازم.",
        "correct": "صحيح"
    },
    {
        "question": "9- تتدهور العملية الزراعية وتنتهي أكثر المزارع حين يوضع أهلها تحت سياسة الإفقار والغرامات الظالمة.",
        "correct": "صحيح"
    }
]

# ==================== دوال البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب والقائمة الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("📚 الدرس 7 و 8 - اختيار من متعدد", callback_data='mcq_7_8')],
        [InlineKeyboardButton("📝 الدرس 7 و 8 - صح وخطأ", callback_data='tf_7_8')],
        [InlineKeyboardButton("📚 المزيد من الأسئلة (قريباً)", callback_data='more')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌟 **بوت أسئلة أنشطة الإدارة في الإسلام** 🌟\n\n"
        "اختر نوع الأسئلة التي تريد اختبار نفسك فيها:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'mcq_7_8':
        context.user_data['questions'] = MCQ_7_8
        context.user_data['current'] = 0
        context.user_data['score'] = 0
        context.user_data['total'] = len(MCQ_7_8)
        context.user_data['type'] = 'mcq'
        await send_question(query, context)
    
    elif query.data == 'tf_7_8':
        context.user_data['questions'] = TF_7_8
        context.user_data['current'] = 0
        context.user_data['score'] = 0
        context.user_data['total'] = len(TF_7_8)
        context.user_data['type'] = 'tf'
        await send_question(query, context)
    
    elif query.data == 'more':
        await query.edit_message_text(
            "📌 سيتم إضافة المزيد من الأسئلة قريباً...\n"
            "تابعونا 👌"
        )

async def send_question(query, context):
    """إرسال السؤال الحالي"""
    idx = context.user_data['current']
    questions = context.user_data['questions']
    
    if idx >= len(questions):
        # انتهى الاختبار
        score = context.user_data['score']
        total = context.user_data['total']
        keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎉 **انتهى الاختبار!**\n\n"
            f"نتيجتك: {score} من {total}\n"
            f"النسبة: {(score/total)*100:.1f}%",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    q = questions[idx]
    
    if context.user_data['type'] == 'mcq':
        keyboard = []
        for opt in q['options']:
            keyboard.append([InlineKeyboardButton(opt, callback_data=f"ans_{opt[0]}")])
        keyboard.append([InlineKeyboardButton("❌ إنهاء", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"**السؤال {idx+1}/{context.user_data['total']}**\n\n{q['question']}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("✅ صحيح", callback_data='ans_صحيح')],
            [InlineKeyboardButton("❌ خطأ", callback_data='ans_خطأ')],
            [InlineKeyboardButton("❌ إنهاء", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"**السؤال {idx+1}/{context.user_data['total']}**\n\n{q['question']}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الإجابات"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back':
        await start(update, context)
        return
    
    if query.data.startswith('ans_'):
        answer = query.data[4:]
        idx = context.user_data['current']
        questions = context.user_data['questions']
        q = questions[idx]
        
        is_correct = (answer == q['correct'])
        
        if is_correct:
            context.user_data['score'] += 1
            feedback = "✅ **إجابة صحيحة!**"
        else:
            feedback = f"❌ **إجابة خاطئة**\nالإجابة الصحيحة: **{q['correct']}**"
        
        context.user_data['current'] += 1
        
        await query.edit_message_text(feedback, parse_mode='Markdown')
        await asyncio.sleep(1)
        await send_question(query, context)

# ==================== تشغيل البوت ====================
def main():
    """النقطة الرئيسية لتشغيل البوت"""
    print("🚀 بدء تشغيل بوت الأسئلة...")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern='^(mcq_|tf_|more|back)$'))
    app.add_handler(CallbackQueryHandler(answer_handler, pattern='^ans_|^back$'))
    
    print("✅ البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()