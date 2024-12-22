from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_location_keyboard(locations: list[list]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i, loc in enumerate(locations):
        country, region, city, key_ = loc
        text_button = f"{city}, {region}, {country}"
        callback_data = f"loc_{i}"
        builder.button(text=text_button, callback_data=callback_data)
    builder.adjust(1)
    return builder.as_markup()


def create_days_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="1 день", callback_data="days_1")
    builder.button(text="3 дня", callback_data="days_3")
    builder.button(text="5 дней", callback_data="days_5")
    builder.adjust(3)
    return builder.as_markup()


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить", callback_data="confirm_yes")
    builder.button(text="Отмена", callback_data="confirm_no")
    builder.adjust(2)
    return builder.as_markup()
