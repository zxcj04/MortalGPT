import os

from . import user_store

TOKEN = os.environ["token"]
ADMIN_CHAT_ID = os.environ["admin_chat_id"]
ADMIN_ID = os.environ["admin_id"]
ADMIN_NAME = os.environ["admin_name"]
OPENAI_API_KEY = os.environ["openai_key"]
LOG_FILE = os.environ["log_file"]
SYSTEM_PROMPT = os.environ["system_prompt"]


def init():
    pass


async def resetUser(context, user_id, chat_id):
    user_store.STORE.reset_user(user_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text="﹝已重置﹞",
    )

    version_updates = user_store.STORE.get_version_updates(user_id)
    if len(version_updates) > 0:
        await context.bot.send_message(
            chat_id=chat_id,
            text="﹝版本更新﹞",
        )
        for update in version_updates:
            await context.bot.send_message(
                chat_id=chat_id,
                text=update,
            )
        await context.bot.send_message(
            chat_id=chat_id,
            text="﹝已更新至最新版本﹞",
        )
        user_store.STORE.update_user_version_to_latest(user_id)
