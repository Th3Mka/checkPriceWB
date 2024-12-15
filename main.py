import asyncio
import logging
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers.commands import router as commands_router
from handlers.callbacks import router as callbacks_router
from handlers.user_handler import router as user_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def main():
    # Загружаем конфигурацию
    config: Config = load_config()

    # Создаем экземпляр бота с токеном
    bot = Bot(token=config.tg_bot.token)

    # Создаем диспетчер без хранилища состояний
    dp = Dispatcher()

    # Подключаем роутеры с обработчиками
    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(user_router)
    # Запускаем бота в режиме опроса
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


