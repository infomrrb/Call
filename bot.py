import asyncio
import random
import re
import io
import csv
from datetime import datetime, timedelta
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =================== কনফিগারেশন ===================
TOKEN = "8753784982:AAFne0Gus1tJJlmF9vR4EOlCF0-BlBB7wv0"  # আপনার টোকেন

# =================== ডেটা জেনারেটর ফাংশন ===================
def generate_random_number():
    prefixes = ['017', '018', '013', '019', '016', '015']
    prefix = random.choice(prefixes)
    number = prefix + str(random.randint(0, 9999999)).zfill(7)
    return number

def generate_random_datetime():
    start = datetime(2024, 5, 11)
    end = datetime(2024, 5, 12)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

def generate_random_status():
    return random.choice(['Missed Call', 'Received Call', 'Dialed Call'])

def generate_call_data(count=100):
    data = []
    for _ in range(count):
        data.append({
            'number': generate_random_number(),
            'status': generate_random_status(),
            'date_time': generate_random_datetime().strftime('%Y-%m-%d %H:%M:%S')
        })
    return data

# =================== বট হ্যান্ডলার ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **স্বাগতম!**\n"
        "আমি একটি কল লিস্ট জেনারেটর বট।\n\n"
        "📱 **কিভাবে ব্যবহার করবেন:**\n"
        "আমাকে একটি বৈধ বাংলাদেশি মোবাইল নম্বর পাঠান (যেমন: `01712345678`)\n"
        "আমি ১০০টি র্যান্ডম কল ডিটেইস তৈরি করব।",
        parse_mode='Markdown'
    )

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    
    # ভ্যালিডেশন
    if not re.match(r'^01[3-9]\d{8}$', phone):
        await update.message.reply_text(
            "❌ **ভুল ফরম্যাট!**\n"
            "দয়া করে ১১ ডিজিটের বৈধ বাংলাদেশি নম্বর দিন (যেমন: `01712345678`)",
            parse_mode='Markdown'
        )
        return

    # প্রসেসিং ইন্ডিকেটর
    await update.message.reply_text("⏳ ডেটা জেনারেট করা হচ্ছে, দয়া করে অপেক্ষা করুন...")

    # ১০০টি ডেটা তৈরি
    data = generate_call_data(100)
    
    # পরিসংখ্যান
    missed = sum(1 for d in data if d['status'] == 'Missed Call')
    received = sum(1 for d in data if d['status'] == 'Received Call')
    dialed = sum(1 for d in data if d['status'] == 'Dialed Call')

    # প্রথম ২০টি ডেটা টেবিল আকারে
    header = "# | নম্বর | স্ট্যাটাস | তারিখ-সময়\n"
    rows = []
    for i, d in enumerate(data[:20], 1):
        rows.append(f"{i} | {d['number']} | {d['status']} | {d['date_time']}")
    table = header + "\n".join(rows)
    
    # মেসেজ তৈরি
    message = (
        f"📊 **পরিসংখ্যান**\n"
        f"🔴 মিসড: {missed}\n"
        f"🟢 রিসিভ: {received}\n"
        f"🔵 ডায়াল: {dialed}\n\n"
        f"📋 **প্রথম ২০টি কল** (মোট {len(data)}টি):\n"
        f"<pre>{table}</pre>"
    )
    if len(data) > 20:
        message += f"\n\n📎 বাকি {len(data)-20}টি ডেটা ফাইল আকারে পাঠানো হচ্ছে..."

    # টেক্সট মেসেজ পাঠান
    await update.message.reply_text(message, parse_mode='HTML')

    # সম্পূর্ণ ডেটা CSV ফাইল হিসেবে তৈরি
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=['number', 'status', 'date_time'])
    writer.writeheader()
    writer.writerows(data)
    csv_buffer.seek(0)
    
    # ফাইল আপলোড
    await update.message.reply_document(
        document=InputFile(csv_buffer, filename='call_list.csv'),
        caption=f"📄 সম্পূর্ণ কল লিস্ট (মোট {len(data)}টি রেকর্ড)"
    )

# =================== মেইন ফাংশন ===================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    print("🤖 বট চালু হয়েছে...")
    app.run_polling()

if __name__ == '__main__':
    main()
