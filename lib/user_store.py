from functools import wraps
import json
import os
import logging

from lib import config


class UserStore:
    _store = {}

    def __init__(self, store={}):
        self._store = store
        self.save()

    @classmethod
    def from_file(cls, path=None):
        store = {}
        if path is None:
            path = os.path.join(os.getcwd(), "user_store.json")
        if not os.path.exists(path):
            return cls()
        with open(path, "r") as f:
            tmp = json.load(f)
            for key in tmp.keys():
                store[int(key)] = tmp[key]
        return cls(store)

    def _to_file(self, path=None):
        if path is None:
            path = os.path.join(os.getcwd(), "user_store.json")
        with open(path, "w") as f:
            json.dump(self._store, f, ensure_ascii=False, indent=4)

    def save(self):
        self._to_file()

    def init_user(self, user_id):
        if user_id not in self._store:
            self.reset_user(user_id)

    def reset_user(self, user_id):
        self.replace_user(
            user_id,
            {
                "messages": [
                    {"role": "system", "content": config.SYSTEM_PROMPT},
                ],
                "name": "",
            },
        )

    def createUserIfNotExist(func=None):
        def do(self, user_id):
            if self.is_user_exist(user_id):
                return
            self.init_user(user_id)

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                user_id = args[0]
                if user_id is None:
                    raise Exception("user_id is None")
            except:
                logging.error("user_id is None")
                return
            do(self, user_id)
            funcResult = func(self, *args, **kwargs)
            return funcResult

        return wrapper

    def is_user_exist(self, user_id) -> bool:
        return user_id in self._store

    @createUserIfNotExist
    def get(self, user_id):
        return self._store.get(user_id)

    def replace_user(self, user_id, user):
        self._store[user_id] = user
        self.save()

    @createUserIfNotExist
    def get_user_name(self, user_id) -> str:
        return self.get(user_id)["name"]

    @createUserIfNotExist
    def set_user_name(self, user_id, name):
        self._store[user_id]["name"] = name
        self.save()

    @createUserIfNotExist
    def get_user_messages(self, user_id):
        return self.get(user_id)["messages"]

    @createUserIfNotExist
    def add_user_message(self, user_id, message):
        self._store[user_id]["messages"].append(message)
        self.save()

    @createUserIfNotExist
    def pop_user_message(self, user_id, index=-1):
        msg = self._store[user_id]["messages"].pop(index)
        self.save()
        return msg

    @createUserIfNotExist
    def is_last_message_by_system(self, user_id) -> bool:
        return self.get(user_id)["messages"][-1]["role"] == "system"

    @createUserIfNotExist
    def pop_to_last_user_message(self, user_id):
        if self.is_last_message_by_system(user_id):
            return None, None
        while self.get(user_id)["messages"][-1]["role"] == "assistant":
            self._store[user_id]["messages"].pop()
        msg = self._store[user_id]["messages"].pop()
        self.save()
        return (msg["role"], msg["content"])
