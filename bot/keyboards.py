from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from math import ceil

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



def create_users_keyboard(users: list, page: int = 1, page_size: int = 10) -> InlineKeyboardBuilder:
    """
    Создаёт клавиатуру с пользователями с пагинацией через InlineKeyboardBuilder
    :param users: список пользователей
    :param page: текущая страница
    :param page_size: количество кнопок на странице
    :return: InlineKeyboardBuilder
    """
    builder = InlineKeyboardBuilder()
    
    total_pages = ceil(len(users) / page_size)
    start = (page - 1) * page_size
    end = start + page_size

    # Добавляем кнопки пользователей
    for user in users[start:end]:
        builder.button(text=user.username, callback_data=f"user:{user.telegram_chat_id}")

    # Кнопки навигации
    if page > 1:
        builder.button(text="⬅️ Назад", callback_data=f"users_page:{page-1}")
    if page < total_pages:
        builder.button(text="Вперед ➡️", callback_data=f"users_page:{page+1}")

    # Упакуем кнопки по 1 в ряд
    builder.adjust(1)
    return builder.as_markup()


def admin_manage_profile(tg_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="удалить профиль", callback_data=f"del_user:{tg_id}")
    builder.button(text="Редактировать профиль", callback_data=f"edit_user:{tg_id}")

    builder.adjust(1)
    return builder.as_markup()

