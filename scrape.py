import requests
from bs4 import BeautifulSoup
import json
import os

VEGAMOVIES_URL = "https://vegamovies.tips"
GPLINK_API = os.environ.get("GPLINK_API")

def shorten_link(url):
    try:
        res = requests.get(f"https://gplinks.in/api?api={GPLINK_API}&url={url}")
        return res.json().get("shortenedUrl", url)
    except:
        return url

def scrape_vegamovies():
    res = requests.get(VEGAMOVIES_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    posts = soup.select('.post-title a')

    data = []

    for post in posts[:30]:
        title = post.get_text().strip()
        link = post['href']

        movie_page = requests.get(link)
        movie_soup = BeautifulSoup(movie_page.text, 'html.parser')

        try:
            poster = movie_soup.select_one('.entry-content img')['src']
        except:
            poster = ""

        qualities = {"480p": "", "720p": "", "1080p": ""}
        for a in movie_soup.find_all('a', href=True):
            text = a.get_text().lower()
            if "480" in text:
                qualities["480p"] = shorten_link(a['href'])
            elif "720" in text:
                qualities["720p"] = shorten_link(a['href'])
            elif "1080" in text:
                qualities["1080p"] = shorten_link(a['href'])

        data.append({
            "title": title,
            "poster": poster,
            "links": qualities
        })

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Scraping complete. Saved to data.json")

if __name__ == "__main__":
    scrape_vegamovies()
