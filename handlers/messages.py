import string
import traceback

from telegram import Update
from telegram.ext import ContextTypes
from opencc import OpenCC

from lib import gpt

cc = OpenCC('s2t')

async def normalChat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_text = update.effective_message.text
    id = await context.bot.send_message(
        chat_id=chat_id,
        text="﹝正在思考﹞",
    )

    now_answer = ""
    full_answer = ""

    answer_generator = gpt.get_answer(user_id, chat_text)
    for answer in answer_generator:
        now_answer = cc.convert(now_answer + answer)

        try:
            is_punctuation = answer in string.punctuation or chr(ord(answer) - 65248) in string.punctuation
        except:
            is_punctuation = False

        if is_punctuation or len(now_answer) - len(full_answer) > 5:
            full_answer = now_answer
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=id.message_id,
                    text=full_answer,
                )
            except Exception as e:
                print(e)
                pass

    if now_answer != full_answer:
        full_answer = now_answer
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=id.message_id,
                text=full_answer,
            )
        except Exception as e:
            print(e)
            pass

    gpt.set_response(user_id, full_answer)
