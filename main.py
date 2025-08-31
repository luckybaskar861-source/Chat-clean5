from pyrogram import Client, filters

# ====== Config ======
API_ID = 25362995
API_HASH = "1bd4bac9f262c3437d2d425a863b1f63"
BOT_TOKEN = "8369273063:AAFCq1SpIqNSlcnEmYeu8pkLeOPbkEjH1pY"
# ====================

app = Client("chat_cleaner_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("clean") & filters.group)
async def clean_messages(client, message):
    """Delete last 10 messages when /clean command is used"""
    chat_id = message.chat.id
    messages = []
    
    async for msg in app.get_chat_history(chat_id, limit=10):
        messages.append(msg.id)

    await app.delete_messages(chat_id, messages)
    await message.reply("✅ Last 10 messages deleted!")


print("🤖 Bot Started...")
app.run()
