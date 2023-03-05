import openai

PREFIX_PROMPT = "你是我的個人助理，請使用繁體中文回答問題。若你認為問題不夠清楚，請跟我說你需要什麼資訊。"

NOW_MESSAGES = [
    {"role": "system", "content": PREFIX_PROMPT},
]

def get_answer(question):
    global NOW_MESSAGES

    NOW_MESSAGES.append({"role": "user", "content": question}),

    responses = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=NOW_MESSAGES,
        stream=True,
    )

    for response in responses:
        try:
            content = response["choices"][0]["delta"]["content"]
            yield content
        except KeyError:
            pass

def set_response(response):
    global NOW_MESSAGES
    NOW_MESSAGES.append({"role": "assistant", "content": response})

def reset():
    global NOW_MESSAGES
    NOW_MESSAGES = [
        {"role": "system", "content": PREFIX_PROMPT},
    ]