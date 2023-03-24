from typing import Optional

from telegram.ext import CallbackContext

from lib import config, errorCatch


async def error_handler(update: Optional[object], context: CallbackContext):
    message = f"{context.user_data} has caused an error: {context.error.__str__()}\nUpdate: {update}"

    errorCatch.logError(context.error)

    try:
        await context.bot.send_message(
            chat_id=config.ADMIN_ID,
            text=message,
        )
    except Exception as e:
        errorCatch.logError(e)
