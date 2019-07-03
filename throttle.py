import time
from urllib import parse


class Throttle:
    def __init__(self, delay=5):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = parse.urlsplit(url).netloc

        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed:
            sleep_secs = self.delay - (time.time() - last_accessed)
            if sleep_secs > 0:
                time.sleep(sleep_secs)

        self.domains[domain] = time.time()
