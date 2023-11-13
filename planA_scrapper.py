from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class Article:
    title: str
    tags: list[str]
    content: str

def extract_article_info(article_url: str) -> Article:
    art_response = requests.get(article_url)
    art_soup = BeautifulSoup(art_response.text, "html.parser")

    # Extract article title
    title = art_soup.find("h1", class_="heading-large").text

    # Extract article tags
    tags = [res.text for res in art_soup.find_all("div", class_="academy-tag-passive w-dyn-item")]

    # Extract article content
    article = art_soup.find("article", class_="article-rich-text w-richtext")
    content: str = "\n".join([p.get_text().encode('latin_1').decode('utf-8') for p in article.children])

    return Article(title, tags, content)

plana_url = "https://plana.earth"
category = "climate-science"
url = f"https://plana.earth/category/{category}"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find article URLs
article_urls = [a["href"] for a in soup.find_all("a", class_="article__teaser-link w-inline-block")]

# Iterate through each article URL and extract the title and content
for article_url in article_urls:
    article = extract_article_info(plana_url + article_url)
    print(f"Title: {article.title}\nTags: {article.tags}\nContent: {article.content}\n")
