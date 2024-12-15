from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon_ru import LEXICON


def create_price_monitoring_keyboard() -> InlineKeyboardMarkup:
    """Создает инлайн клавиатуру для мониторинга цен с кнопками по две в ряд."""
    kb_builder = InlineKeyboardBuilder()

    # Добавляем кнопки по две в ряд
    kb_builder.row(
        InlineKeyboardButton(text=LEXICON['check_price'], callback_data='check_price'),
        InlineKeyboardButton(text=LEXICON['discounts'], callback_data='discounts')
    )

    kb_builder.row(
        InlineKeyboardButton(text=LEXICON['help'], callback_data='help'),
        InlineKeyboardButton(text=LEXICON['settings'], callback_data='settings')
    )

    kb_builder.row(
        InlineKeyboardButton(text=LEXICON['feedback'], callback_data='feedback'),
    )
    kb_builder.row(
        InlineKeyboardButton(text=LEXICON['answers'], callback_data='answers')
    )

    # Возвращаем клавиатуру
    return kb_builder.as_markup()
