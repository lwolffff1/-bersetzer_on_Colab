import requests
from bs4 import BeautifulSoup
import json

def collect_article_links():
    base_url= "https://m.bild.de/?t_ref=https%3A%2F%2Fwww.google.com%2F"
    homepage = requests.get(base_url).text
    soup = BeautifulSoup(homepage, "html.parser")

    # Lấy 5 bài báo mới nhất
    article_links = []
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("https://m.bild.de/"):
            article_links.append(a["href"])
        if len(article_links) == 2:
            break
    # Lưu các links bài báo thành các dict
    links =[{"content":article_links[i], "index": i+1} for i in range(len(article_links))]
    '# Lưu các liên kết vào file JSON'
    with open("article_links.json", "w") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)
    print("📌 Saved article links to article_links.json")

if __name__ == "__main__":
    collect_article_links()