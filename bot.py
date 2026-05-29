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
  
seen = set()  
  
  
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
  
        text = soup.get_text().lower()  
  
        # ===== ФИЛЬТР ПО САЙТАМ =====  
        if "ghb.by" in site:  
            keywords = ["жилой дом"]  
        else:  
            keywords = ["грандичи", "девятовка"]  
  
        if any(k in text for k in keywords):  
            bot.send_message(CHAT_ID, f"🏗 Найдено: {site}")  
  
        # ===== ССЫЛКИ =====  
        links = set()  
  
        for a in soup.find_all("a"):  
            href = a.get("href")  
  
            if not href:  
                continue  
  
            full_url = requests.compat.urljoin(site, href)  
  
            if any(x in full_url for x in ["#", "javascript:", "tel:"]):  
                continue  
  
            links.add(full_url)  
  
        # ===== НОВЫЕ ССЫЛКИ =====  
        new_links = links - seen  
  
        for item in new_links:  
            seen.add(item)  
            bot.send_message(CHAT_ID, f"🆕 Обновление:\n{item}")  
  
  
while True:  
    try:  
        check()  
    except Exception as e:  
        print("Ошибка:", e)  
  
    time.sleep(300)
