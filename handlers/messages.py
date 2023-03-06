import asyncio
import string

from telegram import Update
from telegram.ext import ContextTypes
from opencc import OpenCC
import zhon.hanzi

from lib import gpt, config

cc = OpenCC('s2t')

MESSAGE_LOCKS = {}

async def updateChatToUser(context: ContextTypes.DEFAULT_TYPE, user_id, chat_id, chat_text, message_id):
    now_answer = ""
    full_answer = ""

    try:
        answer_generator = gpt.get_answer(user_id, chat_text)
        for answer in answer_generator:
            now_answer = cc.convert(now_answer + answer)

            try:
                is_punctuation = answer in string.punctuation or answer in zhon.hanzi.punctuation
            except:
                is_punctuation = False

            if is_punctuation or len(now_answer) - len(full_answer) > 10:
                full_answer = now_answer
                try:
                    await context.bot.send_chat_action(
                        chat_id=chat_id,
                        action="typing",
                    )

                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=full_answer,
                    )
                except Exception as e:
                    print(e)
                    pass
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Something went wrong, please try /reset or contact @{config.ADMIN_NAME}",
        )
        return

    if now_answer != full_answer:
        full_answer = now_answer
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=full_answer,
                parse_mode="Markdown",
            )
        except Exception as e:
            print(e)
            pass

    gpt.set_response(user_id, full_answer)

async def updateChatToUserTask(context: ContextTypes.DEFAULT_TYPE, user_id, chat_id, chat_text, message_id):
    if user_id not in MESSAGE_LOCKS:
        MESSAGE_LOCKS[user_id] = asyncio.Lock()

    async with MESSAGE_LOCKS[user_id]:
        await updateChatToUser(context, user_id, chat_id, chat_text, message_id)

async def normalChat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_text = update.effective_message.text
    id = await context.bot.send_message(
        chat_id=chat_id,
        text="﹝正在思考﹞",
    )

    asyncio.get_event_loop().create_task(updateChatToUserTask(context, user_id, chat_id, chat_text, id.message_id))
