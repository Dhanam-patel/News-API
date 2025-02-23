from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from urllib.parse import urljoin

# Load the secret sauce (env vars, baby!)
load_dotenv()
TARGET_WEBSITES = os.getenv("TARGET_WEBSITES", "https://thehackernews.com/,https://www.bleepingcomputer.com/").split(",")

# Unleash the CyberNews-o-Tron 3000!
app = FastAPI(
    title="CyberNews-o-Tron 3000",
    description="Scraping cyber news faster than a hacker downs Red Bull!",
    version="1.0.0"
)

# The mighty scraping engine—fear its power!
def scrape_the_interwebs():
    news_list = []
    headers = {
        "User-Agent": "CyberNews-o-Tron 3000 (Not a bot, I swear—beep boop!)"
    }
    
    for url in TARGET_WEBSITES:
        try:
            print(f"Raiding {url} like a digital pirate—argh!")
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            
            if "thehackernews.com" in url:
                articles = soup.find_all("div", class_="body-post")
                print(f"Found {len(articles)} articles on {url}")
                for article in articles:
                    title_elem = article.find("h2", class_="home-title")
                    link_elem = article.find("a", class_="story-link")
                    title = title_elem.text.strip() if title_elem else "Mystery Scoop!"
                    link = link_elem["href"] if link_elem and link_elem.has_attr("href") else "#"
                    link = urljoin(url, link)
                    news_list.append({
                        "title": title,
                        "link": link,
                        "source": url,
                        "tagline": "Freshly hacked from the cyber vines!"
                    })
            elif "bleepingcomputer.com" in url:
                news_wrap = soup.find("ul", id="bc-home-news-main-wrap")
                if news_wrap:
                    articles = news_wrap.find_all("li")
                    print(f"Found {len(articles)} articles on {url}")
                    for article in articles:
                        text_div = article.find("div", class_="bc_latest_news_text")
                        if text_div:
                            title_elem = text_div.find("h4")
                            if title_elem:
                                if "Sponsored Content" in title_elem.text:
                                    print("Skipping sponsored content")
                                    continue
                                a_tag = title_elem.find("a")
                                if a_tag and a_tag.has_attr("href"):
                                    title = a_tag.text.strip()
                                    link = urljoin(url, a_tag["href"])
                                    news_list.append({
                                        "title": title,
                                        "link": link,
                                        "source": url,
                                        "tagline": "Beep beep—news delivered!"
                                    })
                else:
                    print(f"No news wrap found on {url}")
            else:
                print(f"Unknown website: {url}")
        except Exception as e:
            print(f"Whoops! {url} threw a tantrum: {e}")
    
    return news_list

# Root endpoint—because every API needs a welcome mat
@app.get("/", response_description="Welcome to the cyber party!")
async def root():
    return {
        "greeting": "Hey there, cyber warrior! Welcome to CyberNews-o-Tron 3000!",
        "instructions": "Hit up /news/latest for the hot stuff or /news/category/{something} for picky vibes!"
    }

# Latest news—served hot and spicy!
@app.get("/news/latest", response_description="The freshest cyber gossip!")
async def get_latest_news():
    news = scrape_the_interwebs()
    if not news:
        return {"message": "No news? Guess the hackers are napping—lucky you!"}
    return news

# Category filter—because who doesn’t love a good sort?
@app.get("/news/category/{category}", response_description="News by your fave buzzword!")
async def get_news_by_category(category: str):
    news = scrape_the_interwebs()
    filtered_news = [item for item in news if category.lower() in item["title"].lower()]
    if not filtered_news:
        return {"message": f"No '{category}' news—maybe the cyber world’s gone soft?"}
    return filtered_news
