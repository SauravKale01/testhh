import httpx
from pyrogram import filters, Client, idle
from pyrogram.types import Message
from pymongo import MongoClient

# Replace these with your actual values
API_ID = 19099900
API_HASH = "2b445de78e5baf012a0793e60bd4fbf5"
BOT_TOKEN = "6390766852:AAHAXsP3NHPX2NbnRaFDZA9ZH1h6FyNH1K4"
MONGODB_URI = "mongodb+srv://sonu55:sonu55@cluster0.vqztrvk.mongodb.net/?retryWrites=true&w=majority"
ADMIN_USER_ID = '6198858059'

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB client and database setup
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["my_bot_db"]
user_profiles = db["user_profiles"]

# Dictionary to store the conversation history for each user
conversation_history = {}

@app.on_message(filters.command("start"))
async def start_command(_: Client, message: Message):
    await message.reply(
        "Welcome! I am an AI-Powered Chatbot. Type /chat followed by your message to chat with me!"
    )

@app.on_message(filters.command("chat"))
async def gpt(_: Client, message: Message):
    txt = await message.reply("Typing.......")

    if len(message.command) < 2:
        return await txt.edit("Please provide a message too.")

    query = message.text.split(maxsplit=1)[1]

    # Retrieve conversation history for this user
    chat_id = message.chat.id
    if chat_id in conversation_history:
        dialog_messages = conversation_history[chat_id]
    else:
        dialog_messages = []

    url = "https://api.safone.me/chatgpt"
    payload = {
        "message": query,
        "chat_mode": "assistant",
        "dialog_messages": dialog_messages,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            response = await client.post(
                url, json=payload, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            results = response.json()

            # Check if the API response contains the 'message' key
            if "message" in results:
                bot_response = results["message"]

                # Update conversation history with the latest message
                dialog_messages.append({"bot": bot_response, "user": query})
                conversation_history[chat_id] = dialog_messages

                await txt.edit(bot_response)
            else:
                await txt.edit("**An error occurred. No response received from the API.**")
        except httpx.HTTPError as e:
            await txt.edit(f"**An HTTP error occurred: {str(e)}**")
        except Exception as e:
            await txt.edit(f"**An error occurred: {str(e)}**")

@app.on_message(filters.command("history"))
async def show_history(_: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in conversation_history:
        history = conversation_history[chat_id]
        msg = "\n".join(f"User: {item['user']}\nBot: {item['bot']}\n" for item in history)
        await message.reply(f"Chat History:\n{msg}")
    else:
        await message.reply("Chat history is empty.")

@app.on_message(filters.command("clear_history"))
async def clear_history(_: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in conversation_history:
        conversation_history.pop(chat_id)
        await message.reply("Chat history cleared.")
    else:
        await message.reply("Chat history is already empty.")

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_USER_ID))
async def broadcast(_: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Please provide a message to broadcast.")

    msg_to_broadcast = message.text.split(maxsplit=1)[1]

    # Get all user IDs to broadcast the message
    user_ids = [str(user["_id"]) for user in user_profiles.find({}, {"_id": 1})]

    for user_id in user_ids:
        try:
            await app.send_message(int(user_id), msg_to_broadcast)
        except Exception as e:
            print(f"Failed to send message to user {user_id}: {str(e)}")

@app.on_message(filters.private)
async def process_dm(client: Client, message: Message):
    # Handle DM messages without a specific command
    txt = await message.reply("Typing....")

    query = message.text

    # Retrieve conversation history for this user
    chat_id = message.from_user.id
    if chat_id in conversation_history:
        dialog_messages = conversation_history[chat_id]
    else:
        dialog_messages = []

    url = "https://api.safone.me/chatgpt"
    payload = {
        "message": query,
        "chat_mode": "assistant",
        "dialog_messages": dialog_messages,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            response = await client.post(
                url, json=payload, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            results = response.json()

            # Check if the API response contains the 'message' key
            if "message" in results:
                bot_response = results["message"]

                # Update conversation history with the latest message
                dialog_messages.append({"bot": bot_response, "user": query})
                conversation_history[chat_id] = dialog_messages

                await txt.edit(bot_response)
            else:
                await txt.edit("**An error occurred. No response received from the API.**")
        except httpx.HTTPError as e:
            await txt.edit(f"**An HTTP error occurred: {str(e)}**")
        except Exception as e:
            await txt.edit(f"**An error occurred: {str(e)}**")

# Run the bot
app.run()
idle()
