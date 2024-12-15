import requests
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from database.database import SessionLocal, Feedback
from handlers.user_handler import UserInfoStates
from keyboard.main_menu import create_price_monitoring_keyboard


router = Router()

@router.callback_query(lambda c: c.data == 'feedback')
async def process_feedback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()  # Подтверждаем колбэк
    feedback_text = "Пожалуйста, введите ваш отзыв:"
    await callback_query.message.answer(feedback_text,
                                        reply_markup=types.ReplyKeyboardRemove())  # Убираем инлайн-кнопки
    await state.set_state(UserInfoStates.waiting_for_feedback)  # Устанавливаем состояние ожидания отзыва


@router.message(UserInfoStates.waiting_for_feedback)
async def handle_feedback(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    feedback_message = message.text

    db = SessionLocal()
    new_feedback = Feedback(user_id=user_id, message=feedback_message)

    try:
        db.add(new_feedback)
        db.commit()
        await message.answer("Ваш отзыв успешно сохранен! Спасибо!", reply_markup=create_price_monitoring_keyboard())
    except Exception as e:
        await message.answer("Произошла ошибка при сохранении отзыва.")
        print(f"Ошибка базы данных: {e}")
    finally:
        db.close()

    await state.clear()  # Завершаем состояние после обработки отзыва


@router.callback_query(lambda c: c.data == 'help')
async def process_help(callback_query: CallbackQuery):
    await callback_query.answer()  # Подтверждаем колбэк
    help_text = (
        "Это бот для отслеживания цен на товары. "
        "Вы можете использовать команды для проверки товара или же написать отзыв."
    )
    await callback_query.message.answer(help_text, reply_markup=create_price_monitoring_keyboard())


@router.callback_query(lambda c: c.data == 'answers')
async def process_answers(callback_query: CallbackQuery):
    await callback_query.answer()  # Подтверждаем колбэк
    answers_text = (
        "Вот некоторые ответы на часто задаваемые вопросы:\n"
        "1. Как проверить цену товара?\n"
        "   - Используйте кнопку 'Проверить товар'.\n"
        "2. Как оставить отзыв?\n"
        "   - Нажмите 'Написать отзыв' и введите ваш текст.\n"
        "3. Как получить скидки?\n"
        "   - Нажмите 'Скидки на товары' для получения информации."
    )
    await callback_query.message.answer(answers_text, reply_markup=create_price_monitoring_keyboard())


@router.callback_query(lambda c: c.data == 'discounts')
async def process_discounts(callback_query: CallbackQuery):  # Исправлено имя функции
    await callback_query.answer()  # Подтверждаем колбэк
    discounts_text = (
        "Пока что здесь ничего нет :( "
    )
    await callback_query.message.answer(discounts_text, reply_markup=create_price_monitoring_keyboard())


@router.callback_query(lambda c: c.data == 'check_price')
async def process_check_price(callback_query: CallbackQuery):
    await callback_query.answer()  # Подтверждаем колбэк

    # Здесь ваш код для получения цены товара
    params = {
        'ab_testing': 'false',
        'appType': '1',
        'curr': 'rub',
        'dest': '-5518666',
        'hide_dtype': '10',
        'lang': 'ru',
        'query': 'микрофибра для авто',  # Пример запроса, замените на нужный
        'resultset': 'catalog',
        'sort': 'popular',
        'spp': '30',
    }

    response = requests.get('https://search.wb.ru/exactmatch/ru/common/v9/search', params=params)

    if response.status_code == 200:
        data = response.json()
        products = data.get('data', {}).get('products', [])

        if products:
            # Предположим, что мы просто берем первый продукт для примера
            first_product = products[0]
            product_info = {
                "id": first_product.get("id"),
                "name": first_product.get("name"),
                "brand": first_product.get("brand"),
                "price": first_product['sizes'][0]['price']['total'] / 100,
                "link": f"https://www.wildberries.ru/catalog/{first_product['id']}/detail.aspx"
            }

            response_message = (
                f"Информация о товаре:\n"
                f"ID: {product_info['id']}\n"
                f"Название: {product_info['name']}\n"
                f"Бренд: {product_info['brand']}\n"
                f"Цена: {product_info['price']} руб.\n"
                f"Ссылка на товар: {product_info['link']}"
            )

            await callback_query.message.answer(response_message, reply_markup=create_price_monitoring_keyboard())
        else:
            await callback_query.message.answer("Недостаточно товаров в результате поиска.",
                                                reply_markup=create_price_monitoring_keyboard())
    else:
        await callback_query.message.answer(f"Ошибка при выполнении запроса: {response.status_code}",
                                            reply_markup=create_price_monitoring_keyboard())
