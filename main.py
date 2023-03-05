import logging

from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler

from lib import config, gpt
from handlers import commands, messages

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    config.init()
    gpt.initConfig()

    application = ApplicationBuilder().token(config.TOKEN).build()

    start_handler = CommandHandler("start", commands.start)
    application.add_handler(start_handler)

    reset_handler = CommandHandler("reset", commands.reset)
    application.add_handler(reset_handler)

    test_handler = CommandHandler("test", commands.test)
    application.add_handler(test_handler)

    messages_handler = MessageHandler(filters.CHAT, messages.normalChat)
    application.add_handler(messages_handler)

    unknown_handler = MessageHandler(filters.COMMAND, commands.unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
