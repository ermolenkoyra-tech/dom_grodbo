import time
import requests
import telebot
from bs4 import BeautifulSoup
import os

# ===== ДАННЫЕ =====
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# ===== САЙТЫ =====
sites = [
    "https://grodno.urielt.by/",
    "https://realt.by/belarus/sale/flats/?page=1/",
    "https://realt.by/grodno-region/sale/flats/",
    "https://domovita.by/grodno/flats/sale",
    "https://gohome.by/sale/flat/grodno",
    "https://myrealtor.by/ads",
    "https://www.hommits.by/buy/grodno",
    "https://ghb.by/ru/construction/price_apartments/"
]

seen = set()


def get_pages():
    headers = {"User-Agent": "Mozilla/5.0"}
    pages = []

    for site in sites:
        try:
            r = requests.get(site, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            pages.append((site, soup))
        except Exception as e:
            print("Ошибка сайта:", site, e)

    return pages


def extract_cards(soup):
    cards = []

    # более мягкий и реалистичный фильтр
    for block in soup.find_all(["div", "article", "li"]):

        text = block.get_text(" ", strip=True)

        if not text:
            continue

        # сниженный порог, чтобы не терять объявления
        if len(text) < 40:
            continue

        if not block.find("a", href=True):
            continue

        cards.append(block)

    return cards


def extract_link(card, site):
    a = card.find("a", href=True)
    if a:
        return requests.compat.urljoin(site, a["href"])
    return None


def extract_text(card):
    return card.get_text(" ", strip=True).lower()


def check():
    global seen

    pages = get_pages()

    for site, soup in pages:

        if "https://ghb.by/ru/construction/price_apartments/" in site:
            keywords = ["жилой дом"]
        else:
            keywords = [
                "грандичи",
                "грандичская",
                "белые росы",
                "колбасина",
                "кобринская",
                "лизы чаикиной",
                "янки купалы",
                "кремко",
                "витебская",
                "слонимская",
                "девятовка"
            ]

        cards = extract_cards(soup)

        for card in cards:

            text = extract_text(card)

            if not any(k in text for k in keywords):
                continue

            link = extract_link(card, site)

            if not link:
                continue

            if link in seen:
                continue

            seen.add(link)

            bot.send_message(
                CHAT_ID,
                f"🏗 Найдено:\n{text[:300]}\n{link}"
            )


while True:
    try:
        check()
    except Exception as e:
        print("Ошибка:", e)

    time.sleep(300)
