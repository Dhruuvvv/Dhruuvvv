import openai
from telegram import Update, ReplyKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import pytz
from datetime import datetime
import os
from PyPDF2 import PdfReader
import requests  # For translation API
from textblob import TextBlob  # For sentiment analysis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from pdf2docx import Converter
from docx2pdf import convert as docx_to_pdf
from pathlib import Path
from pptx import Presentation  # For creating PowerPoint files
import comtypes.client  # For PowerPoint to PDF on Windowsfrom pdf2docx import Converter
from pdf2image import convert_from_path
from pptx import Presentation
from docx import Document
import yt_dlp
import time
from yt_dlp import YoutubeDL

# Set up OpenAI API key
openai.api_key = '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'

# Set up Telegram bot token
TELEGRAM_TOKEN = '8094945109:AAEfzkCawPkOskn8O9egPF2PdvI0hxGUCIU'

# To-Do list storage
todo_lists = {}

# Reminder storage
reminders = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! I am your AI-powered bot. How can I assist you today?')
    
    
# Download YouTube Video Handler
async def download_youtube_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video_url = update.message.text.strip()
    
    if 'youtube.com' not in video_url and 'youtu.be' not in video_url:
        await update.message.reply_text("⚠️ Please provide a valid YouTube video or shorts link.")
        return

    await update.message.reply_text("🔄 Downloading video... Please wait.")

    output_dir = './downloads'
    os.makedirs(output_dir, exist_ok=True)  # Ensure the folder exists
    output_path = os.path.join(output_dir, '%(title)s.%(ext)s')

    # Progress hook to track download progress
    def progress_hook(d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percentage = downloaded / total * 100
            speed = d.get('speed', 0) / 1024  # Convert to KB/s
            eta = d.get('eta', 0)

            progress_message = (
                f"📥 Downloading: {percentage:.2f}%\n"
                f"📦 Size: {total / (1024 * 1024):.2f} MB\n"
                f"⚡ Speed: {speed:.2f} KB/s\n"
                f"⏳ ETA: {eta:.2f} sec"
            )

            context.bot.send_message(chat_id=update.effective_chat.id, text=progress_message)

        elif d['status'] == 'finished':
            context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Download completed! Sending the video...")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'quiet': True,
        'progress_hooks': [progress_hook],
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }
        ],
    }

    try:
        start_time = time.time()

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp4')

        elapsed_time = time.time() - start_time
        await update.message.reply_text(f"✅ Download complete in {elapsed_time:.2f} seconds! Sending the video...")

        # Sending the video safely
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

        os.remove(file_path)  # Clean up after sending
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to download video. Error: {e}")

  # Main function to start the bot
def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_youtube_video))
    
    application.run_polling()

if __name__ == "__main__":
    main()
