import os

import openai

TOKEN = os.environ["token"]
ADMIN_ID = os.environ["admin_id"]
ADMIN_NAME = os.environ["admin_name"]
OPENAI_API_KEY = os.environ["openai_key"]

def init():
    openai.api_key = OPENAI_API_KEY
