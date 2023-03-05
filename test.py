import os
from httpcore import stream

import openai

KEY = os.environ["openai_key"]

openai.api_key = KEY

responses = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "請使用繁體中文回答問題。若你認為問題不夠清楚，請跟我說你需要什麼資訊"},
        {"role": "user", "content": "我想知道什麼是機器學習？"}
    ],
    stream=True,
)

for response in responses:
    try:
        content = response["choices"][0]["delta"]["content"]
        print(content, end="", flush=True)
    except KeyError:
        pass
print()