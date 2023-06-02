import json
import os

class DataStore:
    _store = {}
    _store_path = "data_store.json"

    def __init__(self, store={}):
        self._store = store
        self.save()

    @classmethod
    def from_file(cls, path=None):
        store = {}
        if path is None:
            path = os.path.join(os.getcwd(), cls._store_path)
        if not os.path.exists(path):
            return cls()
        with open(path, "r") as f:
            tmp = json.load(f)
            for key in tmp.keys():
                store[key] = tmp[key]
        return cls(store)

    def update_from_file(self, path=None):
        if path is None:
            path = os.path.join(os.getcwd(), self._store_path)
        if not os.path.exists(path):
            return
        with open(path, "r") as f:
            tmp = json.load(f)
            for key in tmp.keys():
                self._store[key] = tmp[key]

    def _to_file(self, path=None):
        if path is None:
            path = os.path.join(os.getcwd(), self._store_path)
        with open(path, "w") as f:
            json.dump(self._store, f, ensure_ascii=False, indent=4)

    def save(self):
        self._to_file()