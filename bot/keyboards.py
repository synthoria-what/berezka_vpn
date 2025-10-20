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

def sub_tariff() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="1", callback_data="sub:first_tariff"), 
                                                      InlineKeyboardButton(text="3", callback_data="sub:third_tariff")],
                                                      [InlineKeyboardButton(text="2", callback_data="sub:second_tariff"),
                                                       InlineKeyboardButton(text="4", callback_data="sub:fourth_tariff")]])
    return keyboard


def current_sub_tariff(invoice_link: str, yookassa_qr_url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    btn_tg_tariff = InlineKeyboardButton(text="Оплатить звездами", url=invoice_link)
    btn_yookassa_qr_payment = InlineKeyboardButton(text="Оплатить по СБП", url=yookassa_qr_url)
    # btn_yookassa_card_payment = InlineKeyboardButton(text="Оплатить СБП", url=yookassa_card_url)

    keyboard.add(btn_tg_tariff)
    keyboard.add(btn_yookassa_qr_payment)
    # keyboard.add(btn_yookassa_card_payment)
    keyboard.adjust(1)

    return keyboard.as_markup()