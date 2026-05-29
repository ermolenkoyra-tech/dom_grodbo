import time
import requests
import telebot
from bs4 import BeautifulSoup
import os

# ===== ДАННЫЕ ИЗ RENDER (сюда НЕ вписываем вручную) =====
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# ===== САЙТ =====
URL = "https://ghb.by/ru/construction/price_apartments/"
KEYWORD = "жилой дом"

bot = telebot.TeleBot(TOKEN)

seen = set()

def get_page():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text().lower()

    links = set()
    for a in soup.find_all("a"):
        href = a.get("href")
        if href:
            links.add(href)

    return text, links


def check():
    global seen

    text, links = get_page()

    # проверка ключевого слова
    if KEYWORD in text:
        bot.send_message(CHAT_ID, f"🏗 Найдено: {KEYWORD}")

    # проверка новых ссылок
    new = links - seen
    for item in new:
        bot.send_message(CHAT_ID, f"🆕 Обновление:\n{item}")

    seen = links


while True:
    try:
        check()
    except Exception as e:
        print("Ошибка:", e)

    time.sleep(300)
