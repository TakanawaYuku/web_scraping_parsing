from bs4 import BeautifulSoup
import requests
import re
import json


def get_head(url: str):
    headers = {
        'Accept':
        '*/*',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
    }
    src = requests.get(url, headers=headers).text

    return BeautifulSoup(src, 'lxml')


def loading_keys(item, all_articles: list, link=None):
    date = item.find("time")["title"][:10]
    title = item.find("h2").find("span").text
    if not link:
        link = f'https://habr.com{item.find("h2").find("a")["href"]}'
    all_articles.append({"date": date, "title": title, "link": link})
    print(f"<{date}><{title}><{link}>")


def get_pattern(pas: list):
    p = ""
    for i in pas:
        p += fr"{i}\w*|"
    pattern = fr"\b({p[:-1]})\b"
    return re.compile(pattern, re.IGNORECASE)


def page_link(start: str = "https://habr.com/ru/all"):
    soup = get_head(start)
    pages = soup.find(class_="tm-pagination__pages").find_all("a")
    return max([int(page.text) for page in pages])


def get_articles(pas, start: str = "https://habr.com/ru/all"):
    pattern = get_pattern(pas)
    i = page_link(start)
    all_articles = []
    for n, url in enumerate([f"{start}/page{i}/" for i in range(1, i + 1)]):
        print(f"Анализ страницы №{n + 1}")
        soup = get_head(url)
        tm_article_snippet = soup.find_all(class_="tm-article-snippet")
        for item in tm_article_snippet:
            if pattern.search(item.text):
                loading_keys(item, all_articles)
    return all_articles


def get_article(pas, start: str = "https://habr.com/ru/all"):
    pattern = get_pattern(pas)
    i = page_link(start)
    all_articles = []
    for i, url in enumerate([f"{start}/page{i}/" for i in range(1, i + 1)]):
        print(f"Анализ страницы №{i + 1}")
        soup = get_head(url)
        tm_article_snippet = soup.find_all(class_="tm-article-snippet")
        for item in tm_article_snippet:
            link = f'https://habr.com{item.find("h2").find("a")["href"]}'
            if pattern.search(item.text):
                loading_keys(item, all_articles, link)
            else:
                soup_next = get_head(link)
                article = soup_next.find(
                    class_=
                    "tm-article-presenter__content tm-article-presenter__content_narrow"
                )
                if pattern.search(article.text):
                    loading_keys(item, all_articles, link)
    return all_articles


def save_json(book: {list, dict}, file: str):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(book, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    KEYWORDS = ['дизайн', 'фото', 'web', 'python']
    articles = get_article(KEYWORDS)
    save_json(articles, "article.json")