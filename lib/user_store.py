from functools import wraps
import logging

from lib import config, version_store
from lib.store import DataStore


class UserStore(DataStore):
    _store_path = "user_store.json"

    def init_user(self, user_id):
        if user_id not in self._store:
            self.reset_user(user_id)

    def reset_user(self, user_id):
        user = self._store.get(user_id, {})
        self.replace_user(
            user_id,
            {
                "messages": [
                    {"role": "system", "content": config.SYSTEM_PROMPT},
                ],
                "version": user.get("version", "0.0.0"),
                "name": user.get("name", ""),
            },
        )
        self.save()

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
            self.save()
            return funcResult

        return wrapper

    def is_user_exist(self, user_id) -> bool:
        return user_id in self._store

    @createUserIfNotExist
    def get(self, user_id):
        return self._store.get(user_id)

    def replace_user(self, user_id, user):
        if user_id not in self._store:
            logging.info("Create user: %s", user_id)
            self._store[user_id] = user
        else:
            for key in user.keys():
                self._store[user_id][key] = user[key]

    @createUserIfNotExist
    def get_user_name(self, user_id) -> str:
        return self.get(user_id)["name"]

    @createUserIfNotExist
    def set_user_name(self, user_id, name):
        self._store[user_id]["name"] = name

    @createUserIfNotExist
    def get_user_messages(self, user_id):
        return self.get(user_id)["messages"]

    @createUserIfNotExist
    def add_user_message(self, user_id, message):
        self._store[user_id]["messages"].append(
            {"role": "user", "content": message}
        )

    @createUserIfNotExist
    def add_assistant_message(self, user_id, message):
        self._store[user_id]["messages"].append(
            {"role": "assistant", "content": message}
        )

    @createUserIfNotExist
    def pop_user_message(self, user_id, index=-1):
        return self._store[user_id]["messages"].pop(index)

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
        return (msg["role"], msg["content"])

    @createUserIfNotExist
    def get_user_version(self, user_id):
        return self.get(user_id)["version"]

    @createUserIfNotExist
    def get_version_updates(self, user_id) -> list:
        return version_store.STORE.get_updates_from_version(
            self.get_user_version(user_id)
        )

    @createUserIfNotExist
    def update_user_version_to_latest(self, user_id):
        self._store[user_id]["version"] = version_store.STORE.get_latest_version()


STORE: UserStore = None


def init():
    global STORE
    s = {}
    tmp = UserStore.from_file()._store
    for user_id in tmp.keys():
        s[int(user_id)] = tmp[user_id]
    STORE = UserStore(s)
