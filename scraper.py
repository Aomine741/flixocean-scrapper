import requests, json, os, time
from bs4 import BeautifulSoup
from github import Github

GP_API = os.environ.get("GPLINK_API")
GITHUB_TOKEN = os.environ.get("GH_TOKEN")
REPO = os.environ.get("GITHUB_REPO")

headers = {'User-Agent': 'Mozilla/5.0'}

def shorten_gplink(url):
    api_url = f"https://gplinks.in/api?api={GP_API}&url={url}"
    try:
        res = requests.get(api_url).json()
        return res.get("shortenedUrl", url)
    except:
        return url

def fetch_posts(base_url):
    r = requests.get(base_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.select("article")[:20]

def scrape_vegamovies():
    base_urls = [
        "https://vegamovies.frl/category/movies/",
        "https://vegamovies.frl/category/web-series/"
    ]
    all_movies = []
    seen_ids = set()

    for url in base_urls:
        try:
            posts = fetch_posts(url)
            for post in posts:
                title_tag = post.select_one('.entry-title a')
                title = title_tag.text.strip()
                link = title_tag['href']
                poster = post.select_one('img')['src']
                movie_id = title.lower().replace(" ", "_")[:50]
                if movie_id in seen_ids:
                    continue
                seen_ids.add(movie_id)

                print(f"🔄 Scraping: {title}")
                movie_page = requests.get(link, headers=headers, timeout=10)
                movie_soup = BeautifulSoup(movie_page.text, 'html.parser')
                desc = movie_soup.select_one('.entry-content p')
                description = desc.text.strip() if desc else "No description"

                links = []
                for a in movie_soup.find_all('a', href=True):
                    href = a['href']
                    if any(q in href.lower() for q in ['480p', '720p', '1080p']):
                        short = shorten_gplink(href)
                        links.append(short)

                if links:
                    all_movies.append({
                        "id": movie_id,
                        "title": title,
                        "poster": poster,
                        "description": description,
                        "quality": "480p / 720p / 1080p",
                        "links": links
                    })
                time.sleep(2)
        except Exception as e:
            print("❌ Error:", e)
    return all_movies

def upload_to_github(data):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO)
    content = json.dumps(data, indent=2)
    try:
        contents = repo.get_contents("data.json")
        repo.update_file(contents.path, "update data", content, contents.sha)
    except:
        repo.create_file("data.json", "create data", content)
    print("✅ data.json pushed to GitHub")

if __name__ == "__main__":
    data = scrape_vegamovies()
    print("✅ Scraped:", len(data))
    upload_to_github(data)
