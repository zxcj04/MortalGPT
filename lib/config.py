import os

from . import gpt

TOKEN = os.environ["token"]
ADMIN_ID = os.environ["admin_id"]
ADMIN_NAME = os.environ["admin_name"]
OPENAI_API_KEY = os.environ["openai_key"]

def init():
    pass

async def resetUser(context, user_id, chat_id):
    gpt.reset(user_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text="﹝已重置﹞",
    )
