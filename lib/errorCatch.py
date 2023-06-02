import logging
import traceback

from telegram import Update
from telegram.ext import ContextTypes

from lib import config, constants


async def callAdminWarning(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
):
    text = f">>> User(@{update.effective_user.username}, {update.effective_user.id}) tried to {text}!"
    logging.warning(text)
    await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=text)


async def sendTryAgainError(
    update: Update, context: ContextTypes.DEFAULT_TYPE, prefix_text=None
):
    text = (
        "Please try again"
        if prefix_text is None
        else prefix_text + " Please try again later"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=constants.INLINE_KEYBOARD_MARKUP_RETRY,
    )


async def sendErrorMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Something went wrong, please retry, reset MortalGPT or contact @{config.ADMIN_NAME}",
        reply_markup=constants.INLINE_KEYBOARD_MARKUP_RETRY_RESET,
    )


def logError(exception: Exception):
    traceback.print_exc()
    template = "An exception of type {0} occurred. Arguments: {1!r}"
    message = template.format(type(exception).__name__, exception.args)
    logging.error(message)


async def sendMessageToAdmin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message: str = None,
    forward_message: bool = False,
    message_id: int = None,
):
    user_name = update.effective_user.username

    message = (
        f">>> User(@{user_name}) <<<\n{message}"
        if message is not None
        else None
    )

    message_id = (
        update.effective_message.message_id
        if message_id is None
        else message_id
    )

    if forward_message:
        try:
            await context.bot.forward_message(
                chat_id=config.ADMIN_CHAT_ID,
                from_chat_id=update.effective_chat.id,
                message_id=message_id,
            )
        except Exception as e:
            logging.warning(f"{e.__str__}")
            logError(e)
            try:
                await context.bot.send_message(
                    chat_id=config.ADMIN_ID,
                    text=f"Error while forwarding message to admin: {e.__str__}",
                )
            except Exception as e:
                logError(e)

    if message is not None:
        try:
            await context.bot.send_message(
                chat_id=config.ADMIN_CHAT_ID,
                text=message,
            )
        except Exception as e:
            logging.warning(f"{e.__str__}")
            logError(e)
            try:
                await context.bot.send_message(
                    chat_id=config.ADMIN_ID,
                    text=f"Error while sending message to admin: {e.__str__}",
                )
            except Exception as e:
                logError(e)
