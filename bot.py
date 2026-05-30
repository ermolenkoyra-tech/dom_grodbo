import time
import requests
import telebot
from bs4 import BeautifulSoup
import os

# ===== ДАННЫЕ =====
TOKEN = os.environ.get("TOKEN")
@bot.message_handler(commands=['restart'])
def restart_search(message):
    global seen, first_run

    seen.clear()
    first_run = False

    bot.reply_to(message, "🔄 Поиск сброшен. При следующей проверке будут заново отправлены все найденные объявления.")
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
first_run = True


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


def check():
    global seen, first_run

    pages = get_pages()

    for site, soup in pages:

        # ===== КЛЮЧЕВЫЕ СЛОВА ПО САЙТАМ =====
        if "ghb.by" in site:
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

        cards = soup.find_all(["h1", "h2", "h3", "a", "p"])

        current_links = set()

        for card in cards:

            text = card.get_text(" ", strip=True).lower()

            if not text:
                continue

            if not any(k in text for k in keywords):
                continue

            link = None

            if card.name == "a":
                link = card.get("href")

            if link:
                link = requests.compat.urljoin(site, link)
            else:
                link = site

            current_links.add(link)

            if first_run:
                continue

            if link in seen:
                continue

            seen.add(link)

            bot.send_message(
                CHAT_ID,
                f"🏗 Найдено:\n\n{text[:300]}\n\n{link}"
            )

        if first_run:
            seen.update(current_links)

    first_run = False


while True:
    try:
        check()
    except Exception as e:
        print("Ошибка:", e)

    time.sleep(300)
