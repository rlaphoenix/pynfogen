import requests


def scrape(url):
    return requests.get(
        url=url,
        headers={
            # pretend to be a normal firefox user, we can't leave anything to chance
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "UPGRADE-INSECURE-REQUESTS": "1"
        }
    ).text
