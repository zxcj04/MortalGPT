import logging
import json
import os

import openai

OPENAI_API_KEY = os.environ["openai_key"]

PREFIX_PROMPT = "你是一個個人助理，請使用繁體中文回答問題。若你認為問題不夠清楚，請跟我說你需要什麼資訊。"

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
            NOW_MESSAGES[user_id] = [
                {"role": "system", "content": PREFIX_PROMPT},
            ]
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

@createUserIfNotExist
def get_answer(user_id, question):
    global NOW_MESSAGES

    NOW_MESSAGES[user_id].append({"role": "user", "content": question}),
    saveConfig()

    try:
        responses = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=NOW_MESSAGES[user_id],
            stream=True,
        )
    except Exception as e:
        logging.error(e)
        raise e

    for response in responses:
        try:
            content = response["choices"][0]["delta"]["content"]
            yield content
        except KeyError:
            pass

@createUserIfNotExist
def set_response(user_id, response):
    global NOW_MESSAGES
    NOW_MESSAGES[user_id].append({"role": "assistant", "content": response})
    saveConfig()

@createUserIfNotExist
def reset(user_id):
    global NOW_MESSAGES
    NOW_MESSAGES[user_id] = [
        {"role": "system", "content": PREFIX_PROMPT},
    ]
    saveConfig()
