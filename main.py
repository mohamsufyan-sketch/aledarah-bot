# bot.py - ملف البوت الرئيسي
import os
import json
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

# ===== إعدادات البوت =====
TOKEN = "YOUR_BOT_TOKEN_HERE"  # ضع توكن البوت هنا

# ===== قاعدة البيانات في الذاكرة =====
user_data = {}
quiz_sessions = {}

# ===== أسئلة البوت (قابلة للتوسع) =====
# يمكنك إضافة المزيد من الأسئلة هنا بسهولة

QUIZ_QUESTIONS = [
    # ===== أسئلة صح/خطأ =====
    {
        "type": "true_false",
        "question": "يُعتَبَرُ مُحافِظُ المَحافَظَةِ وَمَديرُ المَديرِيَّةِ مِنَ العُمّالِ الَّذينَ ذَكَرَهُمُ الإِمامُ عَلِيٌّ (ع) فِي قَولِهِ: (ثُمَّ انظُرْ فِي أُمورِ عِمالِكَ)",
        "answer": True,
        "explanation": "صحيح، يُعتَبَرانِ مِنَ العُمّالِ الَّذينَ يَجِبُ مُراقَبَتُهُم"
    },
    {
        "type": "true_false", 
        "question": "التَّعييناتُ لِلمَسؤولينَ المَبنيَّةُ عَلَى المَيلِ وَالمُجامَلَةِ فَقَط، وَلَيسَ عَلَى الكَفاءَةِ العَملِيَّةِ",
        "answer": False,
        "explanation": "خاطئ، يَجِبُ أَن تَكونَ التَّعييناتُ عَلَى أَساسِ الكَفاءَةِ"
    },
    {
        "type": "true_false",
        "question": "التَّعيينُ فِي المَناصِبِ بِالمُحاباةِ وَالأَثَرَةِ يَعتَبَرُ خِيانَةً",
        "answer": True,
        "explanation": "صحيح، وَهوَ خِيانَةٌ لِلَّهِ سُبحانَهُ وَتَعالى وَلِلنّاسِ"
    },
    {
        "type": "true_false",
        "question": "قَولُ الإِمامِ عَلِيٍّ (ع) (مِن أَهلِ البَيوتاتِ الصّالِحَةِ) يَعني أَن يَكونَ مِن أَهلِ الأَنسابِ وَالأَحسابِ",
        "answer": False,
        "explanation": "خاطئ، يَعني أَن يَكونَ مِمَّن تَرَبّى عَلَى مَكارِمِ الأَخلاقِ"
    },
    {
        "type": "true_false",
        "question": "مِن أَهمِّ ما يَجِبُ مُلاحَظَتُهُ عِندَ الرِّقابَةِ السِّريَّةِ عَلَى المَسؤولِ حُسنُ عَلاقاتِهِ الشَّخصِيَّةِ",
        "answer": False,
        "explanation": "خاطئ، الأَهمُّ أَداؤُهُ لِأَمانَتِهِ المَسؤولِيَّةِ وَوَفاؤُهُ بِالنّاسِ"
    },
    {
        "type": "true_false",
        "question": "قَد يَتَغَيَّرُ بَعضُ المَسؤولينَ مِمَّن كانَ ظاهِرُهُمُ الصَّلاحُ بِسَبَبِ إِصابَتِهِ بِالغُرورِ وَالعُجبِ وَالكِبرِ",
        "answer": True,
        "explanation": "صحيح، وَهذا يَتَطَلَّبُ مُراقَبَةً مُستَمِرَّةً"
    },
    {
        "type": "true_false",
        "question": "أَكثَرُ ما تَكونُ خَياناتُ المَسؤولينَ فِي المالِ وَالإِمكاناتِ",
        "answer": True,
        "explanation": "صحيح، وَهيَ مِن أَشَدِّ الخَياناتِ"
    },
    {
        "type": "true_false",
        "question": "تَراجِعُ اِهتِمامِ المُسلِمينَ بِالزِّراعَةِ بِسَبَبِ سِياساتِ الأَعداءِ الَّتي يَنفُذونَها",
        "answer": True,
        "explanation": "صحيح، وَهذا يَستَدعي تَوعِيَةً وَتَنبيهًا"
    },
    
    # ===== أسئلة اختيار من متعدد =====
    {
        "type": "multiple_choice",
        "question": "مَن أَبرَزَ ما عُرِّفَ عَنِ المَكاتِبِ الحُكومِيَّةِ فِي مَعظَمِ البُلدانِ العَرَبِيَّةِ؟",
        "options": ["تأخير مُعامَلاتِ النّاسِ إِلى حَدٍّ كَبير", "إنجاز مُعامَلاتِ النّاسِ إِلى حَدٍّ مُتَوَسِّط", "كُلُّ ما سَبَقَ صَحيح"],
        "answer": 0,
        "explanation": "التَّأخيرُ مِن أَبرَزِ مَلامِحِ المَكاتِبِ الحُكومِيَّةِ"
    },
    {
        "type": "multiple_choice",
        "question": "ما هِيَ مَواصِفاتُ مَن يَقومونَ بِالرِّقابَةِ؟",
        "options": ["أَهلُ الصِّدقِ وَالوَفاءِ", "مَن لَهُم مَعرفَةٌ بِالأَعمالِ", "كُلُّ ما سَبَقَ صَحيح"],
        "answer": 2,
        "explanation": "يَجِبُ أَن يَكونوا أَهلَ صِدقٍ وَكَفاءَةٍ"
    },
    {
        "type": "multiple_choice",
        "question": "مِمَّا يَجعَلُ النّاسَ يَستَفيدونَ بِشَكلٍ أَكبَرَ مِنَ المُحاصيلِ الزِّراعِيَّةِ؟",
        "options": ["الصِّناعَةُ التَّحويلِيَّة", "إِنتاجُ البُذورِ وَالمَشاتِلِ", "تَصنيعُ الحَراثاتِ وَالحَصّاداتِ"],
        "answer": 0,
        "explanation": "الصِّناعَةُ التَّحويلِيَّةُ تَضيفُ قيمَةً كَبيرَةً لِلزِّراعَةِ"
    },
    
    # ===== أسئلة ملء الفراغات =====
    {
        "type": "fill_blank",
        "question": "قال الإمام علي (ع): (ثُمَّ انظُرْ فِي أُمورِ عِمالِكَ، فَاستَعملْهُمُ اختِباراً وَلا تُوَلِّهِمْ مُحاباةً وَأَثَرَةً، فَإِنَّهُما جِماعٌ مِن شُعَبِ الجَورِ وَالخِيانَةِ)",
        "blank_word": "الجور",
        "hint": "ضد العدل",
        "explanation": "المحاباة والأثرة من شعاب الجور والخيانة"
    },
    {
        "type": "fill_blank",
        "question": "قال الإمام علي (ع): (وَلا تُطَوِّلَنَّ اِحتِجابَكَ عَن رَعِيَّتِكَ، فَإِنَّ اِحتِجابَ الوُلاةِ عَن رَعِيَّتِهِمْ شُعْبَةٌ مِنَ الضَّيقِ وَعَمىً عَنِ الأُمورِ)",
        "blank_word": "الضيق",
        "hint": "ضد السعة",
        "explanation": "الاحتجاب يورث الضيق والعمى عن الأمور"
    },
    {
        "type": "fill_blank",
        "question": "قال الإمام علي (ع): (وَاجْعَلْ لِرَأْسِ كُلِّ أَمْرٍ مِنْ أُمُورِكَ رَأْساً مِنْهُمْ، لا يَقْهَرُهُ كَبِيرُهَا، وَلا يَيْأَسُ مِنْهُ صَغِيرُهَا)",
        "blank_word": "رأساً",
        "hint": "مسؤول",
        "explanation": "يجب تعيين مسؤول لكل أمر"
    }
]

# ===== أوامر البوت =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "مستخدم"
    
    # تهيئة بيانات المستخدم
    if user_id not in user_data:
        user_data[user_id] = {
            "username": username,
            "join_date": datetime.now().isoformat(),
            "total_quizzes": 0,
            "correct_answers": 0,
            "streak": 0,
            "best_score": 0
        }
    
    keyboard = [
        [InlineKeyboardButton("🎯 بدء الاختبار", callback_data="start_quiz")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
    ]
    
    welcome_text = f"""
👋 أهلاً وسهلاً بك *{username}* في بوت اختبارات أنشطة الإدارة في الإسلام!

📚 هذا البوت يتيح لك:
• أسئلة صح/خطأ
• أسئلة اختيار من متعدد  
• أسئلة ملء الفراغات

🎯 اضغط "بدء الاختبار" للبدء!
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المساعدة"""
    help_text = """
📖 *كيفية استخدام البوت:*

1️⃣ اضغط "بدء الاختبار" لبدء جلسة جديدة
2️⃣ اختر نوع الأسئلة المفضل (أو اختبار شامل)
3️⃣ أجب على الأسئلة بالضغط على الأزرار
4️⃣ في أسئلة الفراغات، اكتب الإجابة مباشرة

📊 *النقاط:*
• كل إجابة صحيحة = 10 نقاط
• الإجابة الصحيحة من أول مرة = 5 نقاط إضافية
• سلسلة الإجابات الصحيحة = مضاعف النقاط!

🔄 *الأوامر المتاحة:*
/start - بدء البوت
/quiz - بدء اختبار جديد
/stats - إحصائياتك
/leaderboard - لوحة المتصدرين
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات المستخدم"""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        await update.message.reply_text("❌ لم تبدأ أي اختبار بعد! اضغط /start")
        return
    
    stats = user_data[user_id]
    accuracy = (stats["correct_answers"] / stats["total_quizzes"] * 100) if stats["total_quizzes"] > 0 else 0
    
    stats_text = f"""
📊 *إحصائياتك:*

👤 المستخدم: {stats['username']}
📅 تاريخ الانضمام: {stats['join_date'][:10]}

🎯 إجمالي الأسئلة: {stats['total_quizzes']}
✅ الإجابات الصحيحة: {stats['correct_answers']}
📈 نسبة الصحة: {accuracy:.1f}%
🔥 أطول سلسلة: {stats['streak']}
🏆 أفضل نتيجة: {stats['best_score']}
"""
    await update.message.reply_text(stats_text, parse_mode="Markdown")

# ===== نظام الاختبارات =====

async def start_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء الاختبار من الزر"""
    query = update.callback_query
 أفضل نتيجة: {stats['best_score']}
"""
    await update.message.reply_text(stats_text, parse_mode="Markdown")

# ===== نظام الاختبارات =====

async def start_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء الاختبار من الزر"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("✅ صح/خطأ", callback_data="quiz_tf")],
        [InlineKeyboardButton("📝 اختيار من متعدد", callback_data="quiz_mc")],
        [InlineKeyboardButton("🔤 ملء الفراغات", callback_data="quiz_fb")],
        [InlineKeyboardButton("🎲 اختبار شامل (كل الأنواع)", callback_data="quiz_all")]
    ]
    
    await query.edit_message_text(
        "🎯 *اختر نوع الأسئلة:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def select_quiz_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختيار نوع الاختبار"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    quiz_type = query.data.replace("quiz_", "")
    
    # تصفية الأسئلة حسب النوع
    if quiz_type == "all":
        questions = QUIZ_QUESTIONS.copy()
    elif quiz_type == "tf":
        questions = [q for q in QUIZ_QUESTIONS if q["type"] == "true_false"]
    elif quiz_type == "mc":
        questions = [q for q in QUIZ_QUESTIONS if q["type"] == "multiple_choice"]
    elif quiz_type == "fb":
        questions = [q for q in QUIZ_QUESTIONS if q["type"] == "fill_blank"]
    else:
        questions = QUIZ_QUESTIONS.copy()
    
    random.shuffle(questions)
    questions = questions[:10]  # 10 أسئلة فقط
    
    # إنشاء جلسة اختبار
    quiz_sessions[user_id] = {
        "questions": questions,
        "current": 0,
        "score": 0,
        "correct": 0,
        "wrong": 0,
        "start_time": datetime.now().isoformat(),
        "current_streak": 0
    }
    
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال السؤال الحالي"""
    user_id = update.effective_user.id
    session = quiz_sessions.get(user_id)
    
    if not session or session["current"] >= len(session["questions"]):
        await show_results(update, context)
        return
    
    question = session["questions"][session["current"]]
    q_num = session["current"] + 1
    total = len(session["questions"])
    
    # بناء رسالة السؤال
    header = f"📝 *السؤال [{q_num}/{total}]*\n\n"
    
    if question["type"] == "true_false":
        text = header + f"❓ {question['question']}\n\nاختر:"
        keyboard = [
            [InlineKeyboardButton("✅ صح", callback_data="answer_true"),
             InlineKeyboardButton("❌ خطأ", callback_data="answer_false")]
        ]
        
    elif question["type"] == "multiple_choice":
        text = header + f"❓ {question['question']}\n"
        for i, opt in enumerate(question["options"], 1):
            text += f"\n{i}. {opt}"
        
        keyboard = []
        row = []
        for i in range(len(question["options"])):
            row.append(InlineKeyboardButton(str(i+1), callback_data=f"answer_{i}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
            
    elif question["type"] == "fill_blank":
        text = header + f"🔤 *املأ الفراغ:*\n\n{question['question']}\n\n💡 تلميح: {question['hint']}"
        text += "\n\n✏️ اكتب إجابتك مباشرة..."
        keyboard = [[InlineKeyboardButton("🔄 تخطي", callback_data="skip_question")]]
        
        # تخزين أننا في وضع انتظار رسالة
        session["waiting_for_text"] = True
        
    else:
        return
    
    # إضافة أزرار مساعدة
    keyboard.append([InlineKeyboardButton("🛑 إنهاء الاختبار", callback_data="end_quiz")])
    
    if isinstance(update, Update):
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
            )
    else:
        await update.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إجابة الزر"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    session = quiz_sessions.get(user_id)
    
    if not session:
        await query.edit_message_text("❌ انتهت الجلسة! ابدأ من جديد /quiz")
        return
    
    answer_data = query.data.replace("answer_", "")
    current_q = session["questions"][session["current"]]
    
    # التحقق من الإجابة
    is_correct = False
    
    if current_q["type"] == "true_false":
        user_answer = answer_data == "true"
        is_correct = user_answer == current_q["answer"]
        
    elif current_q["type"] == "multiple_choice":
        user_answer = int(answer_data)
        is_correct = user_answer == current_q["answer"]
    
    await process_answer(update, context, is_correct, current_q)

async def handle_text_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إجابة نصية (ملء الفراغات)"""
    user_id = update.effective_user.id
    session = quiz_sessions.get(user_id)
    
    if not session or not session.get("waiting_for_text"):
        return  # ليس في وضع اختبار
    
    current_q = session["questions"][session["current"]]
    
    if current_q["type"] != "fill_blank":
        return
    
    user_answer = update.message.text.strip()
    correct_answer = current_q["blank_word"]
    
    # التحقق من الإجابة (غير حساس لحالة الأحرف)
    is_correct = user_answer.lower() == correct_answer.lower()
    
    # إزالة وضع الانتظار
    session["waiting_for_text"] = False
    
    await process_answer(update, context, is_correct, current_q, user_answer)

async def process_answer(update, context, is_correct, question, user_answer=None):
    """معالجة الإجابة وتحديث النتائج"""
    user_id = update.effective_user.id
    session = quiz_sessions[user_id]
    
    # تحديث الإحصائيات
    points = 10
    if is_correct:
        session["correct"] += 1
        session["current_streak"] += 1
        # مكافأة السلسلة
        if session["current_streak"] > 2:
            points += session["current_streak"] * 2
        session["score"] += points
        
        # تحديث بيانات المستخدم
        user_data[user_id]["correct_answers"] += 1
        user_data[user_id]["streak"] = max(user_data[user_id]["streak"], session["current_streak"])
        
        result_emoji = "✅"
        result_text = "إجابة صحيحة!"
    else:
        session["wrong"] += 1
        session["current_streak"] = 0
        result_emoji = "❌"
        result_text = "إجابة خاطئة"
    
    user_data[user_id]["total_quizzes"] += 1
    
    # بناء رسالة النتيجة
    explanation = question.get("explanation", "")
    correct_text = ""
    
    if question["type"] == "true_false":
        correct_text = "صح" if question["answer"] else "خطأ"
    elif question["type"] == "multiple_choice":
        correct_text = question["options"][question["answer"]]
    elif question["type"] == "fill_blank":
        correct_text = question["blank_word"]
    
    feedback = f"""
{result_emoji} *{result_text}*

💡 الإجابة الصحيحة: *{correct_text}*
📖 التوضيح: {explanation}

🏆 نقاطك في هذا السؤال: *{points}*
🔥 سلسلة الإجابات الصحيحة: *{session['current_streak']}*
"""
    
    keyboard = [[InlineKeyboardButton("➡️ السؤال التالي", callback_data="next_question")]]
    
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(
            feedback, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            feedback, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الانتقال للسؤال التالي"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    session = quiz_sessions.get(user_id)
    
    if session:
        session["current"] += 1
        await send_question(update, context)

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض نتائج الاختبار"""
    user_id = update.effective_user.id
    session = quiz_sessions.get(user_id)
    
    if not session:
        return
    
    total = len(session["questions"])
    correct = session["correct"]
    wrong = session["wrong"]
    score = session["score"]
    percentage = (correct / total * 100) if total > 0 else 0
    
    # تحديث أفضل نتيجة
    user_data[user_id]["best_score"] = max(user_data[user_id]["best_score"], score)
    
    # تحديد التقييم
    if percentage >= 90:
        grade = "🌟 ممتاز! أداء رائع"
        emoji = "🏆"
    elif percentage >= 70:
        grade = "👏 جيد جداً"
        emoji = "🥈"
    elif percentage >= 50:
        grade = "👍 مقبول"
        emoji = "🥉"
    else:
        grade = "💪 حاول مرة أخرى"
        emoji = "📚"
    
    duration = "غير معروف"
    try:
        start = datetime.fromisoformat(session["start_time"])
        duration = str(datetime.now() - start).split(".")[0]
    except:
        pass
    
    results_text = f"""
{emoji} *نتائج اختبارك:*

📊 الإجابات الصحيحة: *{correct}* من *{total}*
📈 النسبة المئوية: *{percentage:.1f}%*
🏆 مجموع النقاط: *{score}*
⏱️ المدة: {duration}

{grade}

🔥 أطول سلسلة: *{session['current_streak']}* إجابات صحيحة متتالية
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 اختبار جديد", callback_data="start_quiz")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ]
    
    if isinstance(update, Update) and update.callback_query:
        update.callback_query:
        await update.callback_query.edit_message_text(
            results_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            results_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )
    
    # تنظيف الجلسة
    if user_id in quiz_sessions:
        del quiz_sessions[user_id]

async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنهاء الاختبار مبكراً"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("✅ نعم، إنهاء", callback_data="confirm_end")],
        [InlineKeyboardButton("❌ لا، أكمل", callback_data="next_question")]
    ]
    
    await query.edit_message_text(
        "⚠️ هل تريد إنهاء الاختبار؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirm_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأكيد إنهاء الاختبار"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if user_id in quiz_sessions:
        del quiz_sessions[user_id]
    
    keyboard = [
        [InlineKeyboardButton("🎯 اختبار جديد", callback_data="start_quiz")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        "✅ تم إنهاء الاختبار. يمكنك البدء باختبار جديد!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة للقائمة الرئيسية"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎯 بدء الاختبار", callback_data="start_quiz")],
        [InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help_menu")]
    ]
    
    await query.edit_message_text(
        "🏠 *القائمة الرئيسية*\n\nاختر ما تريد:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المساعدة من القائمة"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
📖 *كيفية استخدام البوت:*

1️⃣ اضغط "بدء الاختبار" لبدء جلسة جديدة
2️⃣ اختر نوع الأسئلة المفضل
3️⃣ أجب على الأسئلة
4️⃣ في أسئلة الفراغات، اكتب الإجابة مباشرة

📊 *نظام النقاط:*
• كل إجابة صحيحة = 10 نقاط
• سلسلة الإجابات الصحيحة = مضاعف النقاط!
"""
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    
    await query.edit_message_text(
        help_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

# ===== التشغيل الرئيسي =====

def main():
    """تشغيل البوت"""
    application = Application.builder().token(TOKEN).build()
    
    # الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("quiz", start_quiz_callback))
    
    # معالجات الأزرار
    application.add_handler(CallbackQueryHandler(start_quiz_callback, pattern="^start_quiz$"))
    application.add_handler(CallbackQueryHandler(select_quiz_type, pattern="^quiz_"))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))
    application.add_handler(CallbackQueryHandler(next_question, pattern="^next_question$"))
    application.add_handler(CallbackQueryHandler(end_quiz, pattern="^end_quiz$"))
    application.add_handler(CallbackQueryHandler(confirm_end, pattern="^confirm_end$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(help_menu, pattern="^help_menu$"))
    application.add_handler(CallbackQueryHandler(help_menu, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(stats, pattern="^stats$"))
    application.add_handler(CallbackQueryHandler(next_question, pattern="^skip_question$"))
    
    # معالجة النصوص (لأسئلة الفراغات)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_answer))
    
    print("🤖 البوت يعمل...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
