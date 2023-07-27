import io
import os
import httpx
import time
import requests
import platform
import pyrogram
import sys
from pyrogram import filters, Client, idle
from io import BytesIO
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Replace these with your actual values
API_ID = 19099900
API_HASH = "2b445de78e5baf012a0793e60bd4fbf5"
BOT_TOKEN = "6206599982:AAENkopxhCmzexPq9pZB_gFZcVpOmDXwiNU"
# List of admin users who can perform sensitive commands
ADMIN = [6198858059]  # Replace with actual user IDs of admins


app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store the conversation history for each user
conversation_history = {}

@app.on_message(filters.command("start"))
async def start_command(_: Client, message: Message):
    await message.reply(
        "Welcome! I am an AI-Powered Chatbot. Type /chat followed by your message to chat with me!\nMade With : @BotGeniusHub"
    )

@app.on_message(filters.command("chat"))
async def gpt(_: Client, message: Message):
    txt = await message.reply("💬")

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

@app.on_message(filters.command("bing"))
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



# Record the bot's start time
start_time = time.time()

@app.on_message(filters.command("ping"))
async def ping_pong(_: Client, message: Message):
    # Calculate the bot's ping
    start = time.time()
    message_text = "Pong!🏓"
    msg = await message.reply(message_text)
    end = time.time()
    ping_duration = (end - start) * 1000  # Convert to milliseconds

    # Calculate bot uptime
    uptime_seconds = int(time.time() - start_time)
    uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

    # Add the ping and uptime information to the reply
    await msg.edit(f"{message_text}\n**Ping**: {ping_duration:.2f} ms\n**Uptime**: {uptime_string}")


@app.on_message(filters.command("info"))
async def info_command(_: Client, message: Message):
    # Get information about the user who sent the command
    user = message.from_user
    first_name = user.first_name
    last_name = user.last_name if user.last_name else ""
    user_id = user.id
    username = user.username if user.username else "Not available"
    
    # Get the profile picture of the user
    profile_image = user.photo.big_file_id if user.photo else None
    profile_image_url = None
    
    if profile_image:
        photo = await app.download_media(profile_image)
        profile_image_url = f"Here is your profile picture:\n {photo}"
    
    # Prepare the response message
    bot_info = (
        f"First Name: {first_name}\n"
        f"Last Name: {last_name}\n"
        f"User ID: {user_id}\n"
        f"Username: {username}\n"
    )
    
    # Send the response message
    await message.reply_text(bot_info, disable_web_page_preview=True)
    if profile_image_url:
        with io.BytesIO(profile_image_url.encode()) as bio_file:
            await message.reply_photo(bio_file)



@app.on_message(filters.command("alive"))
async def alive_command(_: Client, message: Message):
    owner_username = "SexyNano"  # Replace with the bot owner's username
    python_version = platform.python_version()
    pyrogram_version = pyrogram.__version__

    bot_info = (
        "🤖 **Bot Is Alive** 🤖\n\n"
        f"👨‍💻 **Owner:** [{owner_username}](https://t.me/{owner_username})\n\n"
        f"🐍 **Python Version:** {python_version}\n\n"
        f"📦 **Pyrogram Version:** {pyrogram_version}\n\n"
        f"🤖 **Bot version:** 1.0.0\n\n"
        f"🏢 **Running on:** {platform.system()} {platform.release()}\n\n"
        f"⏱️ **Uptime:** {get_uptime()}"
    )

    # Add horizontal line
    horizontal_line = "\n" + "=" * 30 + "\n"

    await message.reply_text(horizontal_line + bot_info + horizontal_line)

def get_uptime():
    uptime_seconds = int(time.time() - start_time)
    uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    return uptime_string




print("Bot deployed successfully!")  # Add a log message for successful deployment

# Run the bot
app.run()
idle()
