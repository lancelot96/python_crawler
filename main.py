import re
import time
import queue
import itertools
import threading
import lxml.html as lxml
from urllib import parse, robotparser

import diskcache
import downloader


def get_links(html):
    dom = lxml.fromstring(html)
    return map(lambda a: a.get("href"), dom.cssselect("a"))


def parse_robots(robots_url):
    print(f"robots url {robots_url}")

    try:
        rp = robotparser.RobotFileParser(robots_url)
        rp.read()
        return rp
    except Exception as e:
        print(f"robots parse error {e}")


def threaded_crawler(
        start_url, link_regex, delay=5, robots_url_suffix="robots.txt",
        user_agent="wswp", max_depth=5, scrape_callback=None, num_retries=3,
        cache=None, max_threads=10,
    ):
    seen, robots = {}, {}
    crawler_queue = queue.Queue()

    if isinstance(start_url, list):
        for url in start_url:
            crawler_queue.put(url)
    else:
        crawler_queue.put(start_url)

    headers = {"User-Agent": user_agent}

    D = downloader.Downloader(headers, delay=delay, cache=cache)

    def process():
        while not crawler_queue.empty():
            url = crawler_queue.get()

            protocol, domain, *_ = parse.urlsplit(url)
            robots_url = parse.urlunsplit((protocol, domain, robots_url_suffix, "", ""))
            rp = robots.get(domain) or parse_robots(robots_url)

            if rp and not rp.can_fetch(user_agent, url):
                robots[domain] = rp
                print(f"blocked by robots.txt {url}")
                continue

            html = D(url, num_retries)
            if not html:
                continue

            links = []
            if scrape_callback:
                links = scrape_callback(url, html) or links

            depth = seen.get(url, 0)
            if depth == max_depth:
                print(f"touch max depth {url}")
                continue

            for link in itertools.chain(get_links(html), links):
                if link and re.match(link_regex, link):
                    abs_link = parse.urljoin(url, link)
                    if abs_link not in seen:
                        crawler_queue.put(abs_link)
                        seen[abs_link] = depth + 1

    threads = []
    while not crawler_queue.empty():
        while len(threads) < max_threads and not crawler_queue.empty():
            thread = threading.Thread(target=process)
            thread.setDaemon(True)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        time.sleep(1)


def callback(url=None, html=None):
    dom = lxml.fromstring(html)
    for e in dom.cssselect(".righttxt span"):
        print(e.text_content())


if __name__ == "__main__":
    def read_urls():
        with open("top-500-websites.txt", "r", encoding="utf8") as file:
            return list(map(lambda line: line.strip(), file))

    urls = read_urls()
    threaded_crawler(
        urls, "$^", cache={}, max_threads=10,
    )
