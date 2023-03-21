import logging

from telegram import Update
from telegram.ext import ContextTypes

from lib import config, constants


async def callAdminWarning(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
):
    text = f">>> User(@{update.effective_user.username}, {update.effective_user.id}) tried to {text}!"
    logging.warning(text)
    await context.bot.send_message(chat_id=config.ADMIN_ID, text=text)


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


def logError(exception):
    template = "An exception of type {0} occurred. Arguments: {1!r}"
    message = template.format(type(exception).__name__, exception.args)
    logging.error(message)
