import asyncio
from aiogram import Dispatcher
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router

bot_token = input("Введите BOT-токен: ")
acuweather_api_key = input("Введите API-ключ: ")

router.api_key = acuweather_api_key

async def main():
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
