import requests

import throttle


class Downloader:
    def __init__(self, headers=None, proxies=None, delay=5, cache={}):
        self.headers = headers
        self.proxies = proxies
        self.cache = cache
        self.throttle = throttle.Throttle(delay)

    def __call__(self, url, num_retries=3):
        try:
            result = self.cache[url]
            print(f"loaded from cache {url}")
            return result["html"]
        except Exception:
            print(f"try to download {url}")
            for i in range(num_retries):
                result = self.download(url)
                if result["code"] == 200:
                    if self.cache:
                        self.cache[url] = result

                    return result["html"]

                print(f"download error status")
                if not result["code"] or 400 <= result["code"] < 500:
                    return None

                print(f"retry for {i + 2} times")

    def download(self, url):
        self.throttle.wait(url)

        result = {"html": None, "code": None}
        try:
            resp = requests.get(url, headers=self.headers, proxies=self.proxies)
            result["html"] = resp.text
            result["code"] = resp.status_code
        except requests.RequestException as e:
            print(f"download error {e}")

        return result
