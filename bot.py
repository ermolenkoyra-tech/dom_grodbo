def check():
    global seen

    pages = get_pages()

    for site, soup in pages:

        # ===== ФИЛЬТР ПО САЙТАМ =====
        if "ghb.by" in site:
            keywords = ["жилой дом"]
        else:
            keywords = [
                "грандичи", "грандичская", "белые росы",
                "колбасина", "кобринская", "лизы чаикиной",
                "янки купалы", "кремко", "витебская",
                "слонимская", "девятовка"
            ]

        # ===== ИЩЕМ КАРТОЧКИ ОБЪЯВЛЕНИЙ =====
        cards = soup.find_all(["h1", "h2", "h3", "a", "p"])

        for card in cards:

            text = card.get_text(" ", strip=True).lower()

            if not text:
                continue

            # ===== ПРОВЕРКА КЛЮЧЕВЫХ СЛОВ =====
            if any(k in text for k in keywords):

                link = None
                if card.name == "a":
                    link = card.get("href")

                if link:
                    link = requests.compat.urljoin(site, link)
                else:
                    link = site

                if link in seen:
                    continue

                seen.add(link)

                bot.send_message(
                    CHAT_ID,
                    f"🏗 Найдено:\n{text[:200]}\n{link}"
                )

        # ===== ССЫЛКИ (как запасной вариант) =====
        links = set()

        for a in soup.find_all("a"):
            href = a.get("href")

            if not href:
                continue

            full_url = requests.compat.urljoin(site, href)

            if any(x in full_url for x in ["#", "javascript:", "tel:"]):
                continue

            links.add(full_url)

        new_links = links - seen

        for item in new_links:
            seen.add(item)
            bot.send_message(CHAT_ID, f"🆕 Обновление:\n{item}")
