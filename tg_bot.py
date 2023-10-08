import asyncio
import logging
import os
import sys

from clickhouse_driver import Client
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

logging.basicConfig(
    format="%(levelname)s: %(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)

TOKEN = os.environ.get("APP_TOKEN")

dp = Dispatcher()

connection = Client(
    host="localhost",
    user="default",
    password="",
    port=9000,
    database="todo",
)

@dp.message(Command(commands=["all"]))
async def all_tasks(payload: types.Message):
    ch_all_data = connection.execute("SELECT * FROM todo.todo")

    await payload.reply(
        f"```{pd.DataFrame(ch_all_data, columns=['id', 'text', 'status']).drop('id', axis=1).to_markdown()}```",
        parse_mode="Markdown"
    )


@dp.message(Command(commands=["add"]))
async def add_task(payload: types.Message):
    text = payload.get_args().strip()

    connection.execute(
        "INSERT INTO todo.todo (id, text, status) VALUES (generateUUIDv4(), %(text)s, 'active')",
        {"text": text}
    )

    logging.info("Added a task in the table - %s" % text)
    await payload.reply(f"Added task: *{text}*", parse_mode="Markdown")


@dp.message(Command(commands=["done"]))
async def complete_task(payload: types.Message):
    text = payload.get_args().strip()

    connection.execute(
        "ALTER TABLE todo.todo UPDATE status = 'complete' WHERE text = %(text)s",
        {"text": text}
    )

    logging.info("Completed a task - %s" % text)
    await payload.reply(f"Completed: *{text}*", parse_mode="Markdown")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    