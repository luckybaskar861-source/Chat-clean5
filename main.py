from pyrogram import Client, filters

app = Client(
    "my_bot",
    bot_token="YOUR_BOT_TOKEN",
    api_id=25362995,
    api_hash="1bd4bac9f262c3437d2d425a863b1f63"
)

@app.on_message(filters.command("clean") & filters.group)
async def clean_messages(client, message):
    chat_id = message.chat.id
    
    # delete last 10 messages including command
    for i in range(10):
        try:
            await client.delete_messages(chat_id, message.id - i)
        except:
            pass

app.run()
