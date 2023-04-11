import re
import requests
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import pandas as pd

# function to get list of URLs from Google search results
def get_urls(query):
    url = 'https://www.google.com/search?q=plumbers+in+Boston'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    urls = []
    for g in soup.find_all('div', class_='g'):
        anchors = g.find_all('a')
        if anchors:
            urls.append(anchors[0]['href'])
    for url in urls:
        print(url)
    return urls

if __name__ == "__main__":
    query = ""
    original_url = get_urls(query)
    unscraped = deque(original_url)
    print("got all the links, now to crawl for emails")

    response = ""

    # to save scraped urls
    scraped = []

    # to save fetched emails
    emails = set()

    while len(unscraped):
        url = unscraped.popleft()
        scraped.append(url)

        parts = urlsplit(url)

        base_url = "{0.scheme}://{0.netloc}".format(parts)
        if '/' in parts.path:
            path = url[:url.rfind('/')+1]
        else:
            path = url

        print("Crawling URL %s" % url)
        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.Timeout:
            print("Request for url %s timed out" % url)
            continue
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            print("An error occurred getting the following url: %s" % url)
            continue

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'lxml')
        print("Requested HTTP, now crawling anchors")
        for anchor in soup.find_all("a"):
            if "href" in anchor.attrs:
                link = anchor.attrs["href"]
            else:
                link = ''

            if link.startswith('/'):
                link = base_url + link

            elif not link.startswith('http'):
                link = path + link

            if not link in unscraped and not link in scraped:
                unscraped.append(link)

    print(emails)
