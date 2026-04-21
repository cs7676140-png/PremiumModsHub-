import os
import telebot
from flask import Flask
import threading
from openai import OpenAI

# Load environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")
PORT = int(os.environ.get("PORT", 5000))

# Initialize Flask app (Required by Render)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Telegram Bot is running smoothly on Render!", 200

def start_bot():
    if not BOT_TOKEN:
        return

    bot = telebot.TeleBot(BOT_TOKEN)
    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=HF_TOKEN) if HF_TOKEN else None

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Hello! I am connected to DeepSeek-R1. Send me a message!")

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        if not client:
            bot.reply_to(message, "Error: HF_TOKEN missing.")
            return

        try:
            bot.send_chat_action(message.chat.id, 'typing')
            chat_completion = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1:novita",
                messages=[{"role": "user", "content": message.text}],
            )
            bot.reply_to(message, chat_completion.choices[0].message.content)
        except Exception as e:
            bot.reply_to(message, f"An error occurred: {str(e)}")

    bot.remove_webhook()
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)
