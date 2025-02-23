from fastapi import FastAPI, Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import os
from dotenv import load_dotenv
import json

load_dotenv()
TARGET_WEBSITES = os.getenv("TARGET_WEBSITES", "https://thehackernews.com/,https://cybernews.com/cybercrime/").split(",")

app = FastAPI(
    title="CyberNews-o-Tron 3000",
    description="Scraping cyber news faster than a hacker downs Red Bull!",
    version="1.0.0"
)

def scrape_the_interwebs():
    news_list = []
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver initialized successfully")
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        return [{"error": f"WebDriver setup failed: {str(e)}"}]
    
    try:
        for url in TARGET_WEBSITES[:1]:  # Limit to 1 site
            print(f"Raiding {url} like a digital pirate—argh!")
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                print(f"Timeout waiting for {url} to load!")
                continue
            
            article_links = []
            if "thehackernews.com" in url:
                articles = driver.find_elements(By.CLASS_NAME, "body-post")
                print(f"Found {len(articles)} articles on {url}")
                for article in articles[:5]:  # Limit to 5 articles
                    try:
                        title_elem = article.find_element(By.CLASS_NAME, "home-title")
                        link_elem = article.find_element(By.CLASS_NAME, "story-link")
                        title = title_elem.text.strip() if title_elem else "Mystery Scoop!"
                        link = link_elem.get_attribute("href") if link_elem else "#"
                        if not link.startswith("http"):
                            link = "https://thehackernews.com" + link
                        article_links.append((title, link))
                    except StaleElementReferenceException:
                        print(f"Skipping stale article on {url}")
                        continue
            
            elif "cybernews.com/cybercrime/" in url:
                focus_articles = driver.find_elements(By.CLASS_NAME, "focus-articles__article")
                print(f"Found {len(focus_articles)} focus articles on {url}")
                for article in focus_articles[:5]:  # Limit to 5 articles
                    try:
                        title_elem = article.find_element(By.CLASS_NAME, "focus-articles__title")
                        link_elem = article.find_element(By.CLASS_NAME, "focus-articles__link")
                        title = title_elem.text.strip() if title_elem else "Unnamed Cyber Tale!"
                        link = link_elem.get_attribute("href") if link_elem else "#"
                        if not link.startswith("http"):
                            link = "https://cybernews.com" + link
                        article_links.append((title, link))
                    except StaleElementReferenceException:
                        print(f"Skipping stale focus article on {url}")
                        continue
                
                regular_articles = driver.find_elements(By.CSS_SELECTOR, ".cells__item h3")
                print(f"Found {len(regular_articles)} regular articles on {url}")
                for article in regular_articles[:5]:  # Limit to 5 articles
                    try:
                        link_elem = article.find_element(By.XPATH, "./parent::a")
                        title = article.text.strip() if article.text else "Unnamed Cyber Tale!"
                        link = link_elem.get_attribute("href") if link_elem else "#"
                        if not link.startswith("http"):
                            link = "https://cybernews.com" + link
                        article_links.append((title, link))
                    except StaleElementReferenceException:
                        print(f"Skipping stale regular article on {url}")
                        continue
            
            for title, link in article_links[:5]:  # Double limit for safety
                try:
                    driver.get(link)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    if "thehackernews.com" in url:
                        content_elem = driver.find_element(By.CLASS_NAME, "articlebody")
                        article_text = content_elem.text.strip() if content_elem else "No article found!"
                    elif "cybernews.com/cybercrime/" in url:
                        content_elem = driver.find_element(By.TAG_NAME, "article")
                        article_text = content_elem.text.strip() if content_elem else "No article found!"
                    
                    news_list.append({
                        "title": title,
                        "link": link,
                        "source": url,
                        "article": article_text
                    })
                    if len(news_list) >= 5:  # Limit to 5 total
                        break
                except TimeoutException:
                    print(f"Timeout loading article page: {link}")
                    news_list.append({
                        "title": title,
                        "link": link,
                        "source": url,
                        "article": "Failed to load article due to timeout"
                    })
                    if len(news_list) >= 5:
                        break
                except Exception as e:
                    print(f"Error scraping article {title}: {e}")
                    news_list.append({
                        "title": title,
                        "link": link,
                        "source": url,
                        "article": f"Error fetching article: {str(e)}"
                    })
                    if len(news_list) >= 5:
                        break
            
            if len(news_list) >= 5:
                break
    
    except Exception as e:
        print(f"Whoops! Something went haywire: {e}")
        return [{"error": f"Scraping failed: {str(e)}"}] if not news_list else news_list
    
    finally:
        driver.quit()
    
    return news_list if news_list else [{"error": "No news fetched!"}]

@app.get("/health")
async def health_check():
    return {"status": "API is up and running!"}

@app.get("/")
async def root():
    return {
        "greeting": "Hey there, cyber warrior! Welcome to CyberNews-o-Tron 3000!",
        "instructions": "Hit up /news/all to fetch the latest 5 cyber news articles in JSON!"
    }

@app.get("/news/all")
async def get_all_news():
    news = scrape_the_interwebs()
    if not news or "error" in news[0]:
        return {"message": "No news? Guess the hackers are napping—lucky you!"}
    return Response(content=json.dumps(news), media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
