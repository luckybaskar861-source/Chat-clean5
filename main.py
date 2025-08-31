import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import defaultdict, deque

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ===== Keep-alive tiny web server (Render ku health check) =====
def start_keepalive_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

# ===== Settings =====
MAX_TRACK = 500     # oru chat ku msg ids store pannu
DEFAULT_BULK = 10   # /clean10 default
MAX_BULK = 100      # /clean N max

recent_msgs = defaultdict(lambda: deque(maxlen=MAX_TRACK))

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bot ready!\n"
        "• /clean10 → last 10 msgs delete\n"
        "• /clean N → last N msgs (max 100)\n"
        "• Reply to a msg + /clean N → andha msg irundhu N delete\n"
        "Note: bot ku 'Delete messages' admin permission venum!"
    )

async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg and (msg.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)) and not msg.from_user.is_bot:
        recent_msgs[msg.chat_id].append(msg.message_id)

async def clean10_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await bulk_clean(update, context, DEFAULT_BULK)

async def clean_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = DEFAULT_BULK
    if context.args:
        try:
            n = max(1, min(int(context.args[0]), MAX_BULK))
        except Exception:
            pass
    await bulk_clean(update, context, n)

async def bulk_clean(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int):
    chat = update.effective_chat
    bot = context.bot
    msg = update.effective_message

    if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await msg.reply_text("Group la mattum use panna mudiyum.")
        return

    me = await bot.get_chat_member(chat.id, (await bot.get_me()).id)
    if not me.can_delete_messages:
        await msg.reply_text("Bot ku delete messages permission kudunga.")
        return

    to_delete = []
    if msg.reply_to_message:
        start_id = msg.reply_to_message.message_id
        to_delete = list(range(start_id, start_id + count))
    else:
        recent = recent_msgs[chat.id]
        ids = [m for m in list(recent) if m != msg.message_id]
        to_delete = ids[-count:]

    ok = 0
    for mid in reversed(to_delete):
        try:
            await bot.delete_message(chat.id, mid)
            ok += 1
        except Exception:
            pass

    try:
        await bot.delete_message(chat.id, msg.message_id)
    except Exception:
        pass

    await chat.send_message(f"🧹 Deleted {ok} message(s).", disable_notification=True)

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN missing")

    start_keepalive_server()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("clean10", clean10_cmd))
    app.add_handler(CommandHandler("clean", clean_cmd))
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), remember))
    app.run_polling()

if __name__ == "__main__":
    main()
