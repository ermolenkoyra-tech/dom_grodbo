import time
import requests
import telebot
from bs4 import BeautifulSoup
import os
import json

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("TOKEN или CHAT_ID не заданы")

CHAT_ID = int(str(CHAT_ID).strip())
bot = telebot.TeleBot(TOKEN)

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

# ===== LOAD MEMORY =====
try:
    with open("seen.json", "r") as f:
        seen = set(json.load(f))
except:
    seen = set()


def save_seen():
    try:
        with open("seen.json", "w") as f:
            json.dump(list(seen)[-5000:], f)
    except:
        pass


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ru-RU,ru;q=0.9"
}


def get_pages():
    pages = []

    for site in sites:
        try:
            r = requests.get(site, headers=headers, timeout=12)

            print(site, "->", len(r.text))  # 👈 диагностика

            if len(r.text) < 1000:
                print("⚠️ ПУСТО/АНТИБОТ:", site)
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            pages.append((site, soup))

        except Exception as e:
            print("Ошибка:", site, e)

    return pages


def extract_cards(soup):
    cards = []

    for block in soup.find_all(["article", "div", "li"]):

        text = block.get_text(" ", strip=True)
        if len(text) < 40:
            continue

        if not block.find("a", href=True):
            continue

        cards.append(block)

    return cards


def extract_link(card, site):
    a = card.find("a", href=True)
    if not a:
        return None

    link = requests.compat.urljoin(site, a["href"])

    if any(x in link for x in ["#", "javascript:", "tel:"]):
        return None

    return link


def extract_text(card):
    return card.get_text(" ", strip=True).lower()


def check():
    global seen

    pages = get_pages()

    keywords_base = [
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

    for site, soup in pages:

        keywords = ["жилой дом"] if "ghb.by" in site else keywords_base

        cards = extract_cards(soup)

        for card in cards:

            text = extract_text(card)

            if not any(k in text for k in keywords):
                continue

            link = extract_link(card, site)

            if not link or link in seen:
                continue

            seen.add(link)

            bot.send_message(CHAT_ID, f"🏗 Найдено:\n{text[:300]}\n{link}")

    save_seen()


while True:
    try:
        check()
    except Exception as e:
        print("Ошибка:", e)

    time.sleep(300)
