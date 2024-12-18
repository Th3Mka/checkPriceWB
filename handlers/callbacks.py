import requests
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from database.database import SessionLocal, Feedback, ProductLink
from handlers.user_handler import UserInfoStates
from keyboard.main_menu import create_price_monitoring_keyboard, create_link_management_keyboard

router = Router()


@router.message(lambda message: message.text == '/enter_article')
async def cmd_enter_article(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите артикул или ссылку на товар:")
    await state.set_state(UserInfoStates.waiting_for_article)


@router.message(UserInfoStates.waiting_for_article)
async def process_article(message: types.Message, state: FSMContext):
    input_text = message.text.strip()

    if "wildberries.ru/catalog/" in input_text:
        product_id = input_text.split('/')[-2]
    else:
        product_id = input_text

    headers = {
        'accept': '*/*',
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8',
        'origin': 'https://www.wildberries.ru',
        'referer': f'https://www.wildberries.ru/catalog/{product_id}/detail.aspx',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    response = requests.get(
        f'https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1255987&nm={product_id}',
        headers=headers,
    )

    if response.status_code == 200:
        data = response.json()

        if data.get('data') and data['data'].get('products'):
            product_info = data['data']['products'][0]

            if 'id' in product_info:
                price = product_info['sizes'][0]['price']['total'] / 100
                price_with_wallet = price * 0.98

                response_message = (
                    f"Информация о товаре:\n"
                    f"ID: {product_info['id']}\n"
                    f"Название: {product_info.get('name', 'Не указано')}\n"
                    f"Бренд: {product_info.get('brand', 'Не указано')}\n"
                    f"Цена: {price} руб.\n"
                    f"Цена с WB Кошельком: {price_with_wallet:.2f} руб.\n"
                    f"Ссылка на товар: https://www.wildberries.ru/catalog/{product_info['id']}/detail.aspx\n"
                )
                await message.answer(response_message)

                # Сохраняем информацию о товаре в базу данных
                db = SessionLocal()
                new_product_link = ProductLink(
                    user_id=message.from_user.id,
                    product_id=product_info['id'],
                    link=f"https://www.wildberries.ru/catalog/{product_info['id']}/detail.aspx",
                    name=product_info.get('name', 'Не указано'),
                    brand=product_info.get('brand', 'Не указано'),
                    price=int(price * 100),  # Сохраняем цену в копейках
                    price_with_wallet=int(price_with_wallet * 100)  # Сохраняем цену с кошельком в копейках
                )
                try:
                    db.add(new_product_link)
                    db.commit()
                except Exception as e:
                    await message.answer("Произошла ошибка при сохранении товара.")
                    print(f"Ошибка базы данных: {e}")  # Логируем ошибку для отладки
                finally:
                    db.close()

            else:
                await message.answer("ID товара не найден в ответе.")
        else:
            await message.answer("Товар не найден.")
    else:
        await message.answer(f"Ошибка при выполнении запроса: {response.status_code}")

    await message.answer("Выберите действие:", reply_markup=create_price_monitoring_keyboard())
    await state.clear()


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


@router.callback_query(lambda c: c.data == 'enter_article')
async def process_enter_article(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Пожалуйста, введите артикул или ссылку на товар:")
    await state.set_state(UserInfoStates.waiting_for_article)


@router.callback_query(lambda c: c.data == 'manage_links')
async def process_manage_links(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Выберите действие:", reply_markup=create_link_management_keyboard())


@router.callback_query(lambda c: c.data == 'show_links')
async def process_show_links(callback_query: CallbackQuery):
    await callback_query.answer()  # Подтверждаем колбэк
    db = SessionLocal()

    user_links = db.query(ProductLink).filter(ProductLink.user_id == callback_query.from_user.id).all()

    if user_links:
        links_message = "Ваши сохраненные ссылки:\n"
        for link in user_links:
            links_message += (
                f"ID: {link.id}, "
                f"Название: {link.name}, "
                f"Бренд: {link.brand}, "
                f"Цена: {link.price / 100:.2f} руб., "
                f"Цена с WB Кошельком: {link.price_with_wallet / 100:.2f} руб., "
                f"Ссылка: {link.link}\n"
            )
        await callback_query.message.answer(links_message, reply_markup=create_link_management_keyboard())
    else:
        await callback_query.message.answer("У вас нет сохраненных ссылок.",
                                            reply_markup=create_link_management_keyboard())

    db.close()


@router.callback_query(lambda c: c.data == 'delete_link')
async def process_delete_link(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()  # Подтверждаем колбэк
    await callback_query.message.answer("Введите ID ссылки, которую хотите удалить:")
    # Устанавливаем состояние ожидания ID ссылки
    await state.set_state(UserInfoStates.waiting_for_link_id)


@router.message(UserInfoStates.waiting_for_link_id)
async def process_link_id(message: types.Message, state: FSMContext):
    link_id = message.text.strip()
    db = SessionLocal()
    link_to_delete = db.query(ProductLink).filter(ProductLink.id == link_id,
                                                  ProductLink.user_id == message.from_user.id).first()

    if link_to_delete:
        db.delete(link_to_delete)
        db.commit()
        await message.answer("Ссылка успешно удалена.", reply_markup=create_link_management_keyboard())
    else:
        await message.answer("Ссылка не найдена.", reply_markup=create_link_management_keyboard())

    db.close()
    await state.clear()  # Очищаем состояние после обработки


@router.callback_query(lambda c: c.data == 'back_to_main_menu')
async def process_back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.answer()  # Подтверждаем колбэк
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=create_price_monitoring_keyboard())
