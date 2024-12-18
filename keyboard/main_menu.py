from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon_ru import LEXICON


def create_price_monitoring_keyboard() -> InlineKeyboardMarkup:
    """Создает инлайн клавиатуру для мониторинга цен с кнопками по две в ряд."""
    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(text='Ввести артикул или ссылку', callback_data='enter_article'),
    )

    # Убираем check_price и discounts, добавляем управление ссылками
    kb_builder.row(
        InlineKeyboardButton(text='Управление ссылками', callback_data='manage_links')
    )

    kb_builder.row(
        InlineKeyboardButton(text=LEXICON['help'], callback_data='help'),
        InlineKeyboardButton(text=LEXICON['feedback'], callback_data='feedback')
    )

    return kb_builder.as_markup()


def create_link_management_keyboard() -> InlineKeyboardMarkup:
    """Создает инлайн клавиатуру для управления ссылками на товары."""
    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(text='Показать мои ссылки', callback_data='show_links'),
        InlineKeyboardButton(text='Удалить ссылку', callback_data='delete_link')
    )

    kb_builder.row(
        InlineKeyboardButton(text='Назад', callback_data='back_to_main_menu')
    )

    return kb_builder.as_markup()

