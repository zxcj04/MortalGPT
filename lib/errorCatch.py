import logging

from telegram import Update
from telegram.ext import ContextTypes

from lib import config


async def callAdminWarning(
    update: Update, context: ContextTypes.DEFAULT_TYPE, text: str
):
    text = f">>> User(@{update.effective_user.username}, {update.effective_user.id}) tried to {text}!"
    logging.warning(text)
    await context.bot.send_message(chat_id=config.ADMIN_ID, text=text)


async def sendErrorMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Something went wrong, please contact @{config.ADMIN_NAME}",
    )
