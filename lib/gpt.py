import logging
import json
import os

import openai
from openai.error import OpenAIError
import tiktoken

from lib import constants

OPENAI_API_KEY = os.environ["openai_key"]

PREFIX_PROMPT = constants.SYSTEM_PROMPT

NOW_MESSAGES = {}


def initConfig():
    global NOW_MESSAGES
    openai.api_key = OPENAI_API_KEY
    with open("messages.json", "r") as f:
        tmp = json.load(f)
        for key in tmp.keys():
            NOW_MESSAGES[int(key)] = tmp[key]


def saveConfig():
    with open("messages.json", "w") as f:
        json.dump(NOW_MESSAGES, f, ensure_ascii=False, indent=4)


def createUserIfNotExist(func=None, user_id=None):
    def do(user_id):
        if user_id not in NOW_MESSAGES:
            NOW_MESSAGES[user_id] = {
                "messages": [
                    {"role": "system", "content": PREFIX_PROMPT},
                ],
                "name": "",
            }
            saveConfig()

    def wrapper(*args, **kwargs):
        try:
            user_id = args[0]
            if user_id is None:
                raise Exception("user_id is None")
        except:
            logging.error("user_id is None")
            return
        do(user_id)
        funcResult = func(*args, **kwargs)
        return funcResult

    if func is None:
        if user_id is None:
            raise Exception("No user_id is given")

        do(user_id=user_id)
    else:
        return wrapper


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens


@createUserIfNotExist
def count_user_message_tokens(user_id):
    tokens = 0
    for message in NOW_MESSAGES[user_id]["messages"]:
        tokens += num_tokens_from_string(message["content"])
    return tokens


@createUserIfNotExist
def rotate_user_message(user_id):
    global NOW_MESSAGES
    while count_user_message_tokens(user_id) > 4096 - 1024:
        NOW_MESSAGES[user_id]["messages"].pop(1)
    saveConfig()


@createUserIfNotExist
def get_answer(user_id, question):
    global NOW_MESSAGES

    NOW_MESSAGES[user_id]["messages"].append({"role": "user", "content": question}),
    saveConfig()

    rotate_user_message(user_id)

    try:
        responses = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=NOW_MESSAGES[user_id]["messages"],
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


@createUserIfNotExist
def set_user_name(user_id, name):
    global NOW_MESSAGES
    NOW_MESSAGES[user_id]["name"] = name
    saveConfig()


@createUserIfNotExist
def set_user_message(user_id, message):
    global NOW_MESSAGES
    NOW_MESSAGES[user_id]["messages"].append({"role": "user", "content": message})
    saveConfig()


@createUserIfNotExist
def set_response(user_id, response):
    global NOW_MESSAGES
    NOW_MESSAGES[user_id]["messages"].append({"role": "assistant", "content": response})
    saveConfig()


@createUserIfNotExist
def reset(user_id):
    global NOW_MESSAGES
    NOW_MESSAGES[user_id]["messages"] = [
        {"role": "system", "content": PREFIX_PROMPT},
    ]
    saveConfig()


@createUserIfNotExist
def is_last_message_by_system(user_id):
    return NOW_MESSAGES[user_id]["messages"][-1]["role"] == "system"


@createUserIfNotExist
def pop_to_last_user_message(user_id):
    global NOW_MESSAGES
    if is_last_message_by_system(user_id):
        return None, None
    while NOW_MESSAGES[user_id]["messages"][-1]["role"] == "assistant":
        NOW_MESSAGES[user_id]["messages"].pop()
    msg = NOW_MESSAGES[user_id]["messages"].pop()
    saveConfig()
    return (msg["role"], msg["content"])
