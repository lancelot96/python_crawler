import re
import queue
import lxml.html as lxml
from urllib import parse, robotparser

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


def link_crawler(
        start_url, link_regex, delay=5, robots_url_suffix="robots.txt",
        user_agent="wswp", max_depth=5, scrape_callback=None, num_retries=3,
    ):
    seen = {}
    crawler_queue = queue.Queue()
    crawler_queue.put(start_url)

    headers = {"User-Agent": user_agent}

    D = downloader.Downloader(headers, delay=delay)

    protocol, domain, *_ = parse.urlsplit(start_url)
    robots_url = parse.urlunsplit((protocol, domain, robots_url_suffix, "", ""))
    rp = parse_robots(robots_url)

    while not crawler_queue.empty():
        url = crawler_queue.get()

        if rp and not rp.can_fetch(user_agent, url):
            print(f"blocked by robots.txt {url}")
            continue

        html = D(url, num_retries)
        if not html:
            continue

        if scrape_callback:
            scrape_callback(url, html)

        depth = seen.get(url, 0)
        if depth == max_depth:
            print(f"touch max depth {url}")
            continue

        for link in get_links(html):
            if link and re.match(link_regex, link):
                abs_link = parse.urljoin(url, link)
                if abs_link not in seen:
                    crawler_queue.put(abs_link)
                    seen[abs_link] = depth + 1


def callback(url=None, html=None):
    dom = lxml.fromstring(html)
    for e in dom.cssselect(".righttxt p"):
        print(e.text_content())
        # print(dir(e))
        # exit(1)


if __name__ == "__main__":
    url = "https://alexa.chinaz.com/Country/index_CN.html"
    link_regex = r"index_CN_"

    link_crawler(url, link_regex, scrape_callback=callback)
