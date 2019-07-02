import requests


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


url = "https://movie.douban.com/subject/26727273/episode/1/"

html = download(url)
print(html)
