import requests
import httpx
from pyrogram import filters, Client, idle
from pyrogram.types import Message

# Replace these with your actual values
API_ID = 19099900
API_HASH = "2b445de78e5baf012a0793e60bd4fbf5"
BOT_TOKEN = "6390766852:AAHAXsP3NHPX2NbnRaFDZA9ZH1h6FyNH1K4"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store the conversation history for each user
conversation_history = {}

# List of admin users who can perform sensitive commands
admins = [6198858059]  # Replace with actual user IDs of admins


@app.on_message(filters.command("start"))
async def start_command(_: Client, message: Message):
    user_id = message.from_user.id
    await message.reply(
        "Welcome! I am an AI-Powered Chatbot. "
        "By using this bot, you consent to the collection and storage of your data.\n"
        "Type /chat followed by your message to interact with me or use /help for more options."
    )
    # Prompt the user to choose anonymous usage
    await message.reply("Would you like to use the bot anonymously? (Yes/No)")


@app.on_message(filters.private & filters.regex(r"(?i)^yes$|^no$"))
async def handle_anonymous_usage(_: Client, message: Message):
    user_id = message.from_user.id
    is_anonymous = message.text.lower() == "yes"
    if is_anonymous:
        # User opted for anonymous usage, so we don't need to store user data
        conversation_history.pop(user_id, None)
    await message.reply("You have chosen anonymous usage. Your data won't be stored.")


@app.on_message(filters.command("help"))
async def help_command(_: Client, message: Message):
    help_text = (
        "I am an AI-powered Chatbot bot. Here are the available commands:\n"
        "/start - Start the bot and provide data consent.\n"
        "/help - Show this help message.\n"
        "/chat - Chat with me. Usage: /chat your_message\n"
        "/history - Show chat history.\n"
        "/clear_history - Clear chat history.\n"
        "/delete_data - Request deletion of your data."
    )
    await message.reply(help_text)


@app.on_message(filters.command("delete_data"))
async def delete_data(_: Client, message: Message):
    user_id = message.from_user.id
    if user_id in conversation_history:
        conversation_history.pop(user_id)
        await message.reply("Your data has been deleted.")
    else:
        await message.reply("Your data is already deleted or was not stored.")

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

API_URL = "https://sugoi-api.vercel.app/search"


@app.on_message(filters.command("img"))
async def bing_search(client: Client, message: Message):
    try:
        if len(message.command) == 1:
            await message.reply_text("Please provide a keyword to search.")
            return

        keyword = " ".join(
            message.command[1:]
        )  # Assuming the keyword is passed as arguments
        params = {"keyword": keyword}
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            results = response.json()
            if not results:
                await message.reply_text("No results found.")
            else:
                message_text = ""
                for result in results[:7]:
                    title = result.get("title", "")
                    link = result.get("link", "")
                    message_text += f"{title}\n{link}\n\n"
                await message.reply_text(message_text.strip())
        else:
            await message.reply_text("Sorry, something went wrong with the search.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

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

# Run the bot
app.run()
idle()
