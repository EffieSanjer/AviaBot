import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from handlers import new_direction, check_direction

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(new_direction.router, check_direction.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
