import os
import json
import hashlib


class DiskCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir

    def url_to_path(self, url):
        filename = hashlib.sha256(bytes(url, "utf8")).hexdigest()
        return os.path.join(self.cache_dir, filename)

    def __getitem__(self, url):
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, "r", encoding="utf8") as file:
                return json.load(file)
        else:
            raise KeyError(f"{url} do not exist")

    def __setitem__(self, url, result):
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        path = self.url_to_path(url)
        with open(path, "w", encoding="utf8") as file:
            json.dump(result, file)
