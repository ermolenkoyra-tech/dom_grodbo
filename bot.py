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

seen = set()
print("RESET DONE - bot memory cleared")


def get_pages():
    headers = {"User-Agent": "Mozilla/5.0"}
    pages = []

    for site in sites:
        r = requests.get(site, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        pages.append((site, soup))

    return pages


def extract_card_text(tag):
    """
    Берём не всю страницу, а только локальный текст рядом с ссылкой
    """
    parts = []
    parts.append(tag.get_text(" ", strip=True))

    parent = tag.find_parent()
    if parent:
        parts.append(parent.get_text(" ", strip=True))

    return " ".join(parts).lower()


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

            text_block = extract_card_text(link)

            # ===== GH B (НЕ ТРОГАЕМ) =====
            if "ghb.by" in site:
                if not any(k in text_block for k in DK_KEYWORDS):
                    continue
            else:
                if not any(k in text_block for k in OTHER_KEYWORDS):
                    continue

            # ===== УНИКАЛЬНОСТЬ =====
            if full_url in seen:
                continue

            seen.add(full_url)

            bot.send_message(
                CHAT_ID,
                f"🏠 Найдено:\n{link.get_text(strip=True)}\n{full_url}"
            )


while True:
    try:
        check()
    except Exception as e:
        print("Ошибка:", e)

    time.sleep(300)
