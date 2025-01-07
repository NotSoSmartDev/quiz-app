import logging
import os

import bs4
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    PrefixHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# async def get_games():
#     return [
#         """Когда: 8 января, Среда в 19:30
# Что: Квиз, плиз! MINSK #251
# Описание: Классическая игра с вопросами на всевозможные темы. Здесь реально может пригодиться любое знание, которое вы получали в жизни!
# Где: Ресторан-клуб «Ginger»""",
#         """Когда: 9 января, Четверг в 19:30
# Что: [кино и музыка] MINSK #66
# Описание: Вопросы только про кино и музыку. Меломанам и кинолюбителям посвящается!
# Где: Ресторан-клуб «Ginger»""",
#         """Когда: 14 января, Вторник в 19:30
# Что: Квиз, плиз! [новички] MINSK #49
# Описание: Если вы пока не готовы соперничать с опытными игроками, а занять призовое место хочется — эта игра для вас: играют только начинающие команды с рангом не старше генерала.
# Где: Ресторан-клуб «Ginger»""",
#         """Когда: 15 января, Среда в 19:30
# Что: Квиз, плиз! MINSK #252
# Описание: Классическая игра с вопросами на всевозможные темы. Здесь реально может пригодиться любое знание, которое вы получали в жизни!
# Где: Ресторан-клуб «Ginger»""",
#         """Когда: 16 января, Четверг в 19:30
# Что: [про кино] 2000-х MINSK #1
# Описание: Поймайте ее, если сможете, – нашу новую игру про кинематограф 2000-х!
# Где: Ресторан-клуб «Ginger»""",
#     ]


cl = httpx.AsyncClient(timeout=60)


async def get_games():
    resp = await cl.get("https://minsk.quizplease.ru/schedule")
    html_doc = resp.text

    soup = bs4.BeautifulSoup(html_doc, "html.parser")

    games = []

    games_data = soup.find_all("div", class_="schedule-block")
    for game_data in games_data:
        date_time = (
            game_data.find_all("div", class_="schedule-info")[1]
            .find("div", class_="techtext")
            .text.strip()
        )
        date = game_data.find(
            "div", class_="block-date-with-language-game"
        ).text.strip()
        date = f"{date} {date_time}"
        name = (
            game_data.find("a", class_="schedule-block-head")
            .text.strip()
            .replace("\n", " ")
        )
        desc = game_data.find("div", class_="techtext").text.strip()
        where = game_data.find("div", class_="schedule-block-info-bar").text.strip()

        games.append(f"Когда: {date}\nЧто: {name}\nОписание: {desc}\nГде: {where}")

    return games


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text("Hello")


async def games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update)
    if not update.message:
        return

    games = await get_games()
    await update.message.reply_text("\n\n".join(games))


def main():
    app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

    app.add_handler(PrefixHandler("!", "games", games))

    app.run_polling(allowed_updates=Update.ALL_TYPES)
