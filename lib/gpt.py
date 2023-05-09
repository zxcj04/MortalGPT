import logging
import os
import traceback

import openai
from openai.error import OpenAIError
import tiktoken

from lib import constants
from lib.user_store import UserStore

OPENAI_API_KEY = os.environ["openai_key"]

PREFIX_PROMPT = constants.SYSTEM_PROMPT

STORE: UserStore = None

GPT_VERSION = None


def initConfig():
    global STORE, GPT_VERSION
    openai.api_key = OPENAI_API_KEY
    STORE = UserStore.from_file()

    try:
        model_list = [model.get("id") for model in openai.Model.list().get("data")]
        GPT_VERSION = next(filter(lambda x: x.startswith("gpt-3.5-turbo-"), model_list), None)
    except:
        traceback.print_exc()
        pass


def num_tokens_from_messages(messages):
    """Returns the number of tokens used by a list of messages."""
    model = GPT_VERSION if GPT_VERSION else "gpt-3.5-turbo"
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo" or model == None:
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    else:
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def count_user_message_tokens(user_id):
    return num_tokens_from_messages(STORE.get_user_messages(user_id))


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
