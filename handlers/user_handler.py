from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import SessionLocal, User
from keyboard.main_menu import create_price_monitoring_keyboard

router = Router()

class UserInfoStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_feedback = State()

@router.message(UserInfoStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer("Спасибо, {}! Сколько вам лет?".format(name))
    await state.set_state(UserInfoStates.waiting_for_age)

@router.message(UserInfoStates.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    age_input = message.text
    data = await state.get_data()
    name = data.get('name')

    try:
        age = int(age_input)
        db = SessionLocal()
        existing_user = db.query(User).filter(User.user_id == message.from_user.id).first()

        if existing_user:
            await message.answer("Пользователь уже зарегистрирован.", reply_markup=create_price_monitoring_keyboard())
        else:
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
