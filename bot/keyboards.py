from operator import call
from winreg import KEY_WOW64_32KEY
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def payment_keyboard(link: str | None = None) -> InlineKeyboardMarkup:
    if not link is None:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Оплатить', url=link)]])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Оплатить', callback_data="invalid_payment_link")]])

    return keyboard


def menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Профиль'), KeyboardButton(text='Купить')],
                                             [KeyboardButton(text='Подключиться'), KeyboardButton(text='Помощь')]], resize_keyboard=True)
    
    return keyboard

def sub_rate() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="1", callback_data="first_rate"), 
                                                      InlineKeyboardButton(text="3", callback_data="third_rate")],
                                                      [InlineKeyboardButton(text="2", callback_data="second_rate"),
                                                       InlineKeyboardButton(text="4", callback_data="fourth_rate")]])
    return keyboard


def current_sub_rate(sub_link: str, price: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    btn_tg_sub = InlineKeyboardButton(text="Оплатить звездами", url=sub_link)
    btn_yookassa_payment = InlineKeyboardButton(text="Оплатить с помощью карты", callback_data=f"yookassa_payment:{price}")

    keyboard.add(btn_tg_sub)
    keyboard.add(btn_yookassa_payment)
    keyboard.adjust(1)

    return keyboard.as_markup()