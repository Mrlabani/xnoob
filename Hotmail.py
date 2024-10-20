import os
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from pymegatools import Megatools, MegaError

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Mega tools
mega = Megatools()

# Status messages and bot settings
class Messages:
    download_name = "N/A"
    status_head = "Download Status:"

class Paths:
    down_path = "downloads/"

# Ensure download directory exists
if not os.path.exists(Paths.down_path):
    os.makedirs(Paths.down_path)

# Start command for Telegram bot
async def start(update: Update, context):
    await update.message.reply_text("Welcome to Mega.nz Downloader Bot! Send me a Mega.nz link to download.")

# Mega.nz download handler
async def megadl(update: Update, context):
    link = update.message.text  # Get Mega.nz link from the message
    chat_id = update.message.chat_id
    
    if not link.startswith("https://mega.nz/"):
        await update.message.reply_text("Please send a valid Mega.nz link.")
        return
    
    await update.message.reply_text("Processing the Mega link...")

    try:
        # Start the download
        await mega.async_download(link, progress=pro_for_mega, path=Paths.down_path)
        file_path = os.path.join(Paths.down_path, Messages.download_name)
        
        # Send the downloaded file to the user
        await context.bot.send_document(chat_id=chat_id, document=open(file_path, 'rb'))

    except MegaError as e:
        logger.error(f"Error during Mega download: {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"An error occurred: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await context.bot.send_message(chat_id=chat_id, text="An unexpected error occurred.")

# Function to handle progress and status updates
async def pro_for_mega(stream, process):
    line = stream[-1]
    try:
        # Parse progress details
        details = line.split(":")
        file_name = details[0]
        progress_details = details[1].split()

        percentage = float(progress_details[0][:-1])
        downloaded_size = f"{progress_details[2]} {progress_details[3]}"
        total_size = f"{progress_details[7]} {progress_details[8]}"
        speed = f"{progress_details[9][1:]} {progress_details[10][:-1]}"

        Messages.download_name = file_name
        
        # ETA calculation
        eta = "Unknown"
        try:
            remaining_bytes = float(progress_details[7]) - float(progress_details[2])
            bytes_per_second = float(progress_details[9][1:]) * (1024 if progress_details[10][-1] == 'K' else 1)
            remaining_seconds = remaining_bytes / bytes_per_second if bytes_per_second != 0 else 0
            eta = getTime(remaining_seconds)
        except Exception as e:
            logger.warning(f"ETA calculation error: {e}")

        # Display the progress status in the Telegram chat
        status_message = (f"📥 Downloading from Mega.nz\n"
                          f"🏷️ File: {file_name}\n"
                          f"📊 Progress: {percentage}%\n"
                          f"⬇️ Downloaded: {downloaded_size} of {total_size}\n"
                          f"🚀 Speed: {speed}\n"
                          f"⏳ ETA: {eta}")
        # Send or update the message in the chat
        # Consider storing the message_id to edit it later
        
        return status_message
        
    except Exception as e:
        logger.error(f"Error parsing Mega download progress: {e}")

# Helper function to format ETA
def getTime(seconds):
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

# Main function to run the bot
async def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Get the bot token from an environment variable
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), megadl))

    # Run the bot
    await application.run_polling()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
      
