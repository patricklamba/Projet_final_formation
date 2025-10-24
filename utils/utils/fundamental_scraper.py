import requests
from bs4 import BeautifulSoup

class FundamentalScraper:
    BASE_URL = "https://www.investing.com/economic-calendar/"

    @staticmethod
    def fetch_news(symbol="XAUUSD"):
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(FundamentalScraper.BASE_URL, headers=headers)
        if resp.status_code != 200:
            raise ConnectionError(f"Erreur connexion : {resp.status_code}")

        soup = BeautifulSoup(resp.text, "html.parser")
        news_items = soup.find_all("tr", class_="js-event-item")
        news_texts = []
        for item in news_items[:5]:
            title = item.get("data-event", "")
            impact = item.get("data-impact", "")
            news_texts.append(f"{impact} : {title}")
        return "\n".join(news_texts)
