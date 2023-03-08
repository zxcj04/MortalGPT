import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from lib import errorCatch, config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="嗨，我是你的個人助理。",
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await errorCatch.callAdminWarning(
        update, context, text=f"use command {update.effective_message.text}"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="抱歉，我不知道你在說什麼。",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    await config.resetUser(context, user_id, chat_id)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="﹝測試中﹞",
    )
