import logging
import os

import openai
from openai.error import OpenAIError
import tiktoken

from lib import constants
from lib.user_store import UserStore

OPENAI_API_KEY = os.environ["openai_key"]

PREFIX_PROMPT = constants.SYSTEM_PROMPT

STORE: UserStore = None


def initConfig():
    global STORE
    openai.api_key = OPENAI_API_KEY
    STORE = UserStore.from_file()


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def count_user_message_tokens(user_id):
    tokens = 0
    for message in STORE.get_user_messages(user_id):
        tokens += num_tokens_from_string(message["content"])
    return tokens


def rotate_user_message(user_id):
    while count_user_message_tokens(user_id) > 4096 - 1024:
        STORE.pop_user_message(user_id, 1)


def get_answer(user_id, question):
    STORE.add_user_message(user_id, {"role": "user", "content": question})

    rotate_user_message(user_id)

    try:
        responses = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=STORE.get_user_messages(user_id),
            stream=True,
            timeout=30,
            max_tokens=1024,
        )
    except OpenAIError as e:
        if e.code == "context_length_exceeded":
            logging.error("Context length exceeded")
        raise e
    except Exception as e:
        raise e

    for response in responses:
        try:
            content = response["choices"][0]["delta"]["content"]
            yield content
        except KeyError:
            pass


def set_user_name(user_id, name):
    STORE.set_user_name(user_id, name)


def set_user_message(user_id, message):
    STORE.add_user_message(user_id, {"role": "user", "content": message})


def set_response(user_id, response):
    STORE.add_user_message(user_id, {"role": "assistant", "content": response})


def pop_last_message(user_id):
    STORE.pop_user_message(user_id)


def reset(user_id):
    STORE.reset_user(user_id)


def is_last_message_by_system(user_id):
    return STORE.is_last_message_by_system(user_id)


def pop_to_last_user_message(user_id):
    return STORE.pop_to_last_user_message(user_id)
