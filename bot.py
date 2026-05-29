import time
import requests
import telebot
from bs4 import BeautifulSoup
import os
import re

# ===== ДАННЫЕ =====
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# ===== САЙТЫ =====
sites = [
    "https://grodno.urielt.by/",
    "https://realt.by/grodno-region/sale/flats/",
    "https://domovita.by/grodno/flats/sale",
    "https://gohome.by/sale/flat/grodno",
    "https://myrealtor.by/ads",
    "https://www.hommits.by/buy/grodno",
    "https://ghb.by/ru/construction/price_apartments/"
]

# ===== НАСТРОЙКИ =====
DK_KEYWORDS = ["жилой дом"]
OTHER_KEYWORDS = ["грандичи", "девятовка"]

MIN_PRICE = 150000
MAX_PRICE = 200000

seen = set()
print("RESET DONE - bot memory cleared")


def extract_price(text):
    """
    ищем цену в тексте (BYN, руб, €, $)
    """
    numbers = re.findall(r"\d{3,9}", text.replace(" ", ""))
    prices = [int(n) for n in numbers]

    if not prices:
        return None

    return min(prices)


def get_pages():
    headers = {"User-Agent": "Mozilla/5.0"}
    pages = []

    for site in sites:
        r = requests.get(site, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        pages.append((site, soup))

    return pages


def check():
    global seen

    pages = get_pages()

    for site, soup in pages:

        links = soup.find_all("a")

        for link in links:
            href = link.get("href")
            if not href:
                continue

            full_url = requests.compat.urljoin(site, href)

            if any(x in full_url for x in ["#", "javascript:", "tel:"]):
                continue

            text_block = (link.get_text(" ", strip=True) + " " +
                          (link.find_parent().get_text(" ", strip=True) if link.find_parent() else "")
                          ).lower()

            # ===== ЦЕНА =====
            price = extract_price(text_block)

            if price is None:
                continue

            if not (MIN_PRICE <= price <= MAX_PRICE):
                continue

            # ===== ФИЛЬТРЫ =====
            if "ghb.by" in site:
                if not any(k in text_block for k in DK_KEYWORDS):
                    continue
            else:
                if not any(k in text_block for k in OTHER_KEYWORDS):
                    continue

            # ===== ДУБЛИКАТЫ =====
            if full_url in seen:
                continue

            seen.add(full_url)

            bot.send_message(
                CHAT_ID,
                f"🏠 Найдено\nЦена: {price} BYN\n{link.get_text(strip=True)}\n{full_url}"
            )


while True:
    try:
        check()
    except Exception as e:
        print("Ошибка:", e)

    time.sleep(300)
