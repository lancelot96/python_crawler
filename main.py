import re
import queue
import requests
import lxml.html as lxml
from urllib import parse, robotparser


import throttle


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


def download(url, headers, num_retries=3, proxies=None):
    print(f"try to download {url}")

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


def link_crawler(
        start_url, link_regex, delay=5, robots_url_suffix="robots.txt",
        user_agent="wswp", max_depth=5, scrape_callback=None,
    ):
    seen = {}
    crawler_queue = queue.Queue()
    crawler_queue.put(start_url)

    headers = {"User-Agent": user_agent}

    download_throttle = throttle.Throttle(delay)

    protocol, domain, *_ = parse.urlsplit(start_url)
    robots_url = parse.urlunsplit((protocol, domain, robots_url_suffix, "", ""))
    rp = parse_robots(robots_url)

    while not crawler_queue.empty():
        url = crawler_queue.get()

        if rp and not rp.can_fetch(user_agent, url):
            continue

        download_throttle.wait(url)
        html = download(url, headers=headers)

        if scrape_callback:
            scrape_callback(url, html)

        depth = seen.get(url, 0)
        if depth == max_depth:
            continue

        for link in get_links(html):
            if link and re.match(link_regex, link):
                abs_link = parse.urljoin(url, link)
                if abs_link not in seen:
                    crawler_queue.put(abs_link)
                    seen[abs_link] = depth + 1


def callback(url=None, html=None):
    dom = lxml.fromstring(html)
    with open("top-500-websites.txt", "a+", encoding="utf8") as file:
        for e in dom.cssselect(".righttxt span"):
            file.write(f"http://{e.text_content()}\n")


if __name__ == "__main__":
    url = "https://alexa.chinaz.com/Country/index_CN.html"
    link_regex = r"index_CN_"

    link_crawler(url, link_regex, 0, scrape_callback=callback)
