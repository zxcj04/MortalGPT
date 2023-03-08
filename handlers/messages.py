import asyncio
import string

from telegram import Update
from telegram.ext import ContextTypes
from opencc import OpenCC
import zhon.hanzi

from lib import gpt, config, errorCatch, constants

cc = OpenCC("s2t")

MESSAGE_LOCKS = {}
PUNCTUATIONS = [*string.punctuation, *zhon.hanzi.punctuation , "\n", "\r"]


async def editMsg(
    context: ContextTypes.DEFAULT_TYPE, chat_id, message_id, text
):
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
        )
    except Exception as e:
        print(e)
        pass


async def updateChatToUser(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message_id
):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_text = update.effective_message.text

    now_answer = ""
    full_answer = ""

    try:
        answer_generator = gpt.get_answer(user_id, chat_text)
        for answer in answer_generator:
            now_answer = cc.convert(now_answer + answer)

            try:
                is_punctuation = answer in PUNCTUATIONS
            except:
                is_punctuation = False

            if is_punctuation and len(now_answer) - len(full_answer) > 10:
                full_answer = now_answer
                try:
                    await context.bot.send_chat_action(
                        chat_id=chat_id,
                        action="typing",
                    )

                    await editMsg(context, chat_id, message_id, full_answer)
                except Exception as e:
                    print(e)
                    pass
    except Exception as e:
        await errorCatch.sendErrorMessage(context, e)
        return

    if now_answer != full_answer:
        full_answer = now_answer
        try:
            await editMsg(context, chat_id, message_id, full_answer)
        except Exception as e:
            print(e)
            pass

    await context.bot.editMessageText(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=constants.INLINE_KEYBOARD_MARKUP_DONE,
        text=full_answer,
    )

    gpt.set_response(user_id, full_answer)


async def updateChatToUserTask(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message_id
):
    global MESSAGE_LOCKS

    user_id = update.effective_user.id

    if user_id not in MESSAGE_LOCKS:
        MESSAGE_LOCKS[user_id] = asyncio.Lock()

    async with MESSAGE_LOCKS[user_id]:
        await updateChatToUser(update, context, message_id)


async def normalChat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    id = await context.bot.send_message(
        chat_id=chat_id,
        text="﹝正在思考﹞",
    )

    asyncio.get_event_loop().create_task(
        updateChatToUserTask(update, context, id.message_id)
    )


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == constants.CallBackType.RESET:
        await config.resetUser(
            context, query.from_user.id, query.message.chat_id
        )
    elif query.data == constants.CallBackType.DONE:
        user_id = query.from_user.id
        if user_id not in MESSAGE_LOCKS:
            MESSAGE_LOCKS[user_id] = asyncio.Lock()

        async with MESSAGE_LOCKS[user_id]:
            await context.bot.send_sticker(
                chat_id=query.message.chat_id,
                sticker=constants.DONE_STICKER,
            )


async def chatOtherFallback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="﹝不知道要怎麼回答﹞",
    )
