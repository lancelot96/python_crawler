import re
import time
import queue
import requests
from urllib import parse


def get_links(html):
    # <a href="?discussion_start=10#comment-section">2</a>
    web_regex = re.compile(r"<a +href=[\'\"](.*?)[\'\"]")
    return web_regex.findall(html)


def download(url, num_retries=3, user_agent="wswp", proxies=None):
    print(f"try to download {url}")

    headers = {"User-Agent": user_agent}

    for i in range(num_retries):
        try:
            resp = requests.get(url, headers=headers, proxies=proxies)
            if resp.status_code == 200:
                return resp.text

            print(f"download error status code {resp.status_code}")
            if 500 <= resp.status_code < 600:
                print(f"retry for {i + 2} times")
        except requests.RequestException as e:
            print(f"download error {e}")
            break


def link_cwraler(start_url, link_regex, delay=5):
    seen = set()
    crawler_queue = queue.Queue()
    crawler_queue.put(start_url)

    while not crawler_queue.empty():
        url = crawler_queue.get()

        time.sleep(delay)
        html = download(url)
        # TODO

        for link in get_links(html):
            if link and re.match(link_regex, link):
                abs_link = parse.urljoin(url, link)
                if abs_link not in seen:
                    crawler_queue.put(abs_link)
                    seen.add(abs_link)


url = "https://movie.douban.com/subject/26727273/episode/1/"
link_regex = r"\?discussion_start="


link_cwraler(url, link_regex)
