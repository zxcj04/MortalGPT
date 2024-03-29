import logging
from logging.handlers import RotatingFileHandler

from telegram.ext import (
    filters,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
)

from lib import config, gpt, user_store, version_store
from handlers import commands, messages, error

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=128 * 1024 * 1,
            backupCount=5,
        )
    ],
)

logging.getLogger("httpx").setLevel(logging.WARNING)


if __name__ == "__main__":
    config.init()
    user_store.init()
    version_store.init()
    gpt.init()

    application = (
        ApplicationBuilder()
        .token(config.TOKEN)
        .http_version(http_version="1.1")
        .get_updates_http_version(get_updates_http_version="1.1")
        .build()
    )

    start_handler = CommandHandler("start", commands.start)
    application.add_handler(start_handler)

    reset_handler = CommandHandler("reset", commands.reset)
    application.add_handler(reset_handler)

    test_handler = CommandHandler("test", commands.test)
    application.add_handler(test_handler)

    unknown_handler = MessageHandler(filters.COMMAND, commands.unknown)
    application.add_handler(unknown_handler)

    messages_handler = MessageHandler(filters.TEXT, messages.normalChat)
    application.add_handler(messages_handler)

    video_handler = MessageHandler(filters.VIDEO, messages.videoChat)
    application.add_handler(video_handler)

    audio_handler = MessageHandler(filters.AUDIO, messages.audioChat)
    application.add_handler(audio_handler)

    record_audio_handler = MessageHandler(filters.VOICE, messages.voiceChat)
    application.add_handler(record_audio_handler)

    file_handler = MessageHandler(filters.Document.ALL, messages.fileChat)
    application.add_handler(file_handler)

    chat_other_handler = MessageHandler(
        filters.ALL, messages.chatOtherFallback
    )
    application.add_handler(chat_other_handler)

    callback_handler = CallbackQueryHandler(callback=messages.callback)
    application.add_handler(callback_handler)

    application.add_error_handler(error.error_handler)

    application.run_polling()
