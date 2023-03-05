import logging

import openai

PREFIX_PROMPT = "你是我的個人助理，請使用繁體中文回答問題。若你認為問題不夠清楚，請跟我說你需要什麼資訊。"

NOW_MESSAGES = {}

def createUserIfNotExist(func=None, user_id=None):
    def do(user_id):
        if user_id not in NOW_MESSAGES:
            NOW_MESSAGES[user_id] = [
                {"role": "system", "content": PREFIX_PROMPT},
            ]

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

    responses = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=NOW_MESSAGES[user_id],
        stream=True,
    )

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

@createUserIfNotExist
def reset(user_id):
    global NOW_MESSAGES
    NOW_MESSAGES[user_id] = [
        {"role": "system", "content": PREFIX_PROMPT},
    ]
