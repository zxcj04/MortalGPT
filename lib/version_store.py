from functools import wraps

from lib.store import DataStore

class VersionStore(DataStore):
    _store_path = "version_store.json"

    def clsDefaultDecorator(func=None):
        def do(self):
            self.update_from_file()
            if "versions" not in self._store:
                self._store["versions"] = {
                    "0.0.0": "Initial version",
                }
            versions = self._store["versions"].keys()
            self._store["version_list"] = sorted(versions, key=lambda x: [int(i) for i in x.split(".")])

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            do(self)
            funcResult = func(self, *args, **kwargs)
            self.save()
            return funcResult

        return wrapper

    @clsDefaultDecorator
    def get_latest_version(self):
        return self._store["version_list"][-1]

    @clsDefaultDecorator
    def get_latest_version_description(self):
        return self._store["versions"][self.get_latest_version()]

    @clsDefaultDecorator
    def get_version_list(self) -> list:
        return self._store["version_list"]

    @clsDefaultDecorator
    def get_version_description(self, version):
        if version not in self._store["versions"]:
            return None
        return self._store["versions"][version]

    @clsDefaultDecorator
    def get_updates_from_version(self, version):
        version_list = self.get_version_list()
        if version not in version_list:
            return None
        version_index = version_list.index(version)
        version_updates = [f"{v}: {self.get_version_description(v)}" for v in version_list[version_index + 1:]]
        return version_updates


STORE: VersionStore = None


def init():
    global STORE
    STORE = VersionStore.from_file()