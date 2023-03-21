import logging
from typing import Optional

from telegram.ext import CallbackContext

from lib import config

async def error_handler(update: Optional[object], context: CallbackContext):
    message = f"{context.user_data} has caused an error: {context.error.__str__()}\nUpdate: {update}"

    logging.error(context.error)

    try:
        await context.bot.send_message(
            chat_id=config.ADMIN_ID,
            text=message,
        )
    except Exception as e:
        logging.error(e)
