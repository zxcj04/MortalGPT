from io import BufferedReader
import logging
import os
import traceback

import openai
from openai.error import OpenAIError
import tiktoken

from lib import user_store

OPENAI_API_KEY = os.environ["openai_key"]

GPT_VERSION = None


def init():
    global GPT_VERSION
    openai.api_key = OPENAI_API_KEY

    try:
        model_list = [
            model.get("id") for model in openai.Model.list().get("data")
        ]
        GPT_VERSION = next(
            filter(lambda x: x.startswith("gpt-3.5-turbo-"), model_list), None
        )
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
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    else:
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
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
    return num_tokens_from_messages(
        user_store.STORE.get_user_messages(user_id)
    )


def rotate_user_message(user_id):
    while count_user_message_tokens(user_id) > 4096 - 1024:
        user_store.STORE.pop_user_message(user_id, 1)


def get_answer(user_id, question):
    user_store.STORE.add_user_message(user_id, question)

    rotate_user_message(user_id)

    try:
        responses = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=user_store.STORE.get_user_messages(user_id),
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


def get_whisper_api_answer(target_file: BufferedReader):
    try:
        transcription = openai.Audio.transcribe("whisper-1", target_file)
        answer = transcription["text"]
        return answer
    except Exception as e:
        raise e
