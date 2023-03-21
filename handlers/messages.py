import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes
from openai.error import OpenAIError

from lib import gpt, config, errorCatch, constants



MESSAGE_LOCKS = {}

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
        errorCatch.logError(e)
        pass


async def updateChatToUser(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message_id, isRetry=False
):
    user_id = update.effective_user.id
    user_name = update.effective_user.name
    chat_id = update.effective_chat.id
    chat_text = update.effective_message.text

    gpt.set_user_name(user_id, user_name)

    if isRetry:
        logging.info(f"User {user_name} is retrying")

        _, chat_text = gpt.pop_to_last_user_message(user_id)

        if chat_text is None:
            try:
                await editMsg(context, chat_id, message_id, "﹝不知道要怎麼回答﹞")
                return
            except Exception as e:
                errorCatch.logError(e)
                pass

    now_answer = ""
    full_answer = ""

    is_code_block = False

    try:
        formated_chat_text = chat_text.replace("\n", "\\n")
        logging.info(f"User {user_name} ask: {formated_chat_text}")
        answer_generator = gpt.get_answer(user_id, chat_text)
        for answer in answer_generator:
            now_answer = constants.CC.convert(now_answer + answer)

            for c in answer:
                if c == "`":
                    is_code_block = not is_code_block

            try:
                is_punctuation = any([p in answer for p in constants.PUNCTUATIONS]) or answer in constants.PUNCTUATIONS
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

                    if "\n" in answer and not is_code_block:
                        id = await context.bot.send_message(
                            chat_id=chat_id,
                            text="﹝正在思考﹞",
                            disable_notification=True,
                        )
                        message_id = id.message_id
                        full_answer = ""
                        now_answer = ""

                except Exception as e:
                    errorCatch.logError(e)
                    pass

    except OpenAIError as e:
        await errorCatch.sendTryAgainError(update, context, e.user_message)
        return
    except Exception as e:
        errorCatch.logError(e)
        await errorCatch.sendErrorMessage(update, context)
        return

    if now_answer != full_answer:
        full_answer = now_answer
        try:
            await editMsg(context, chat_id, message_id, full_answer)
        except Exception as e:
            errorCatch.logError(e)
            pass

    await context.bot.editMessageText(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=constants.INLINE_KEYBOARD_MARKUP_DONE_RETRY,
        text=full_answer,
    )

    gpt.set_response(user_id, full_answer)
    logging.info(f"Answered to User {user_name}")


async def updateChatToUserTask(
    update: Update, context: ContextTypes.DEFAULT_TYPE, isRetry=False
):
    global MESSAGE_LOCKS

    user_id = update.effective_user.id

    if user_id not in MESSAGE_LOCKS:
        MESSAGE_LOCKS[user_id] = asyncio.Lock()

    async with MESSAGE_LOCKS[user_id]:
        chat_id = update.effective_chat.id
        id = await context.bot.send_message(
            chat_id=chat_id,
            text="﹝正在思考﹞",
            disable_notification=True,
        )

        await updateChatToUser(update, context, id.message_id, isRetry)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE, isRetry=False):
    asyncio.get_event_loop().create_task(
        updateChatToUserTask(update, context, isRetry)
    )


async def normalChat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await chat(update, context)


async def retryChat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await chat(update, context, isRetry=True)


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
    elif query.data == constants.CallBackType.RETRY:
        await retryChat(update, context)


async def chatOtherFallback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="﹝不知道要怎麼回答﹞",
    )
