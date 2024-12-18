from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from database.database import SessionLocal, User
from handlers.user_handler import UserInfoStates
from keyboard.main_menu import create_price_monitoring_keyboard

router = Router()

@router.message(lambda message: message.text == '/start')
async def cmd_start(message: types.Message, state: FSMContext):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.user_id == message.from_user.id).first()

    if existing_user:
        # Если пользователь уже зарегистрирован, показываем инлайн-кнопки
        await message.answer("Добро пожаловать обратно, {}!".format(existing_user.name),
                             reply_markup=create_price_monitoring_keyboard())
    else:
        # Если пользователь не зарегистрирован, запрашиваем имя
        await message.answer("Здравствуйте! 👋 Как вас зовут?")
        await state.set_state(UserInfoStates.waiting_for_name)  # Устанавливаем состояние ожидания имени

    db.close()  # Закрываем соединение с базой данных


@router.message(lambda message: message.text == '/help')
async def cmd_help(message: types.Message):
    help_text = (
        "Это бот для отслеживания цен на товары. "
        "Вы можете использовать команды для проверки товара или же написать отзыв."
    )
    await message.answer(help_text, reply_markup=create_price_monitoring_keyboard())


@router.message(lambda message: message.text == '/feedback')
async def cmd_feedback(message: types.Message, state: FSMContext):
    feedback_text = "Пожалуйста, введите ваш отзыв:"
    await message.answer(feedback_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(UserInfoStates.waiting_for_feedback)

@router.message(UserInfoStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text  # Получаем имя пользователя
    await state.update_data(name=name)  # Сохраняем имя в состоянии

    await message.answer("Спасибо, {}! Сколько вам лет?".format(name))
    await state.set_state(UserInfoStates.waiting_for_age)  # Устанавливаем состояние ожидания возраста


@router.message(UserInfoStates.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    age_input = message.text  # Получаем возраст пользователя
    data = await state.get_data()  # Получаем данные из состояния
    name = data.get('name')  # Извлекаем имя

    try:
        age = int(age_input)  # Пробуем преобразовать возраст в int
        db = SessionLocal()

        # Проверяем существует ли пользователь с таким user_id
        existing_user = db.query(User).filter(User.user_id == message.from_user.id).first()
        if existing_user:
            await message.answer("Пользователь уже зарегистрирован.", reply_markup=create_price_monitoring_keyboard())
        else:
            # Сохраняем информацию о пользователе в базе данных
            new_user = User(user_id=message.from_user.id, name=name, age=age)
            db.add(new_user)
            db.commit()
            await message.answer("Ваше имя: {}, ваш возраст: {} лет.".format(name, age),
                                 reply_markup=create_price_monitoring_keyboard())

    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст (число).")
    except Exception as e:
        await message.answer("Произошла ошибка при сохранении информации о пользователе.")
        print(f"Ошибка базы данных: {e}")
    finally:
        db.close()

    await state.clear()
