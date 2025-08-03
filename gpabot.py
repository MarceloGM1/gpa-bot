import telebot
from flask import Flask, request
import re
import os

TOKEN = os.environ.get("TOKEN", "8021716368:AAEOgKiI0DFV3DyHDeHHWWULWCh0TSV0qlU")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/", methods=['GET'])
def index():
    return "البوت شغال ✅", 200

def grade_to_points(grade):
    if grade >= 20: return 4.0
    elif grade >= 19: return 3.8
    elif grade >= 18: return 3.6
    elif grade >= 17: return 3.4
    elif grade >= 16: return 3.2
    elif grade >= 15: return 3.0
    elif grade >= 14: return 2.8
    elif grade >= 13: return 2.6
    elif grade >= 12: return 2.4
    elif grade >= 11: return 2.0
    else: return 0.0

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = []
    bot.reply_to(message,
        "👋 اهلا بيك!\n\n"
        "ابعتلي المواد واحدة واحدة أو كلها مرة واحدة بصيغة:\n\n"
        "`اسم المقرر : ...`\n"
        "`عدد الساعات المعتمدة : ...`\n"
        "`الدرجة : ...`\n\n"
        "ولما تخلص ابعت `/احسب` علشان احسبلك المعدل.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['احسب'])
def calculate(message):
    user_id = message.chat.id
    if user_id not in user_data or not user_data[user_id]:
        bot.reply_to(message, "مفيش بيانات! ابعتلي مواد الأول.")
        return

    total_points = 0
    total_hours = 0
    response = ""
    
    for course in user_data[user_id]:
        name = course['name']
        hours = course['hours']
        grade = course['grade']
        points = grade_to_points(grade)
        total_points += points * hours
        total_hours += hours
        response += f"📘 *{name}*\n  الدرجة: {grade} → النقاط: {points}\n\n"

    gpa = total_points / total_hours
    response += f"📊 *المعدل التراكمي (GPA):* `{round(gpa, 2)}`"
    bot.reply_to(message, response, parse_mode='Markdown')
    user_data[user_id] = []  # نفضي البيانات بعد الحساب

@bot.message_handler(func=lambda message: True)
def handle_course_input(message):
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = []

    text = message.text
    pattern = r"اسم المقرر\s*[:：]\s*(.*?)\n.*?عدد الساعات(?: المعتمدة)?\s*[:：]?\s*(\d+(?:[.,]?\d*)?)\n.*?الدرجة\s*[:：]?\s*(\d+(?:[.,]?\d*)?)"
    matches = re.findall(pattern, text, re.IGNORECASE)

    if not matches:
        bot.reply_to(message, "❗ صيغة غير مفهومة. استخدم النموذج:\n\nاسم المقرر : ...\nعدد الساعات المعتمدة : ...\nالدرجة : ...")
        return

    for name, hours, grade in matches:
        try:
            course = {
                'name': name.strip(),
                'hours': float(hours.replace(",", ".")),
                'grade': float(grade.replace(",", "."))
            }
            user_data[user_id].append(course)
        except:
            bot.reply_to(message, f"⚠️ في مشكلة في المادة: {name}")
            return

    bot.reply_to(message, "✅ تم إضافة المادة. ابعت مواد تانية أو اكتب /احسب لحساب المعدل.")