from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, LabeledPrice, CallbackQuery
from data.models.users import User
from keyboards import *
from config import config, TariffConfig
from logger import Logger
from payments import *
from proxy_client import ProxyClient
from data.sql_queries import SqlQueries
from datetime import datetime
from functools import wraps

from faker import Faker

logger = Logger.getinstance()
router = Router()
bot = Bot(config.tg_token)
tariff_config = TariffConfig()
proxy = ProxyClient()
faker = Faker()
sql_queries = SqlQueries()


ADMIN_IDS = [863618184]


def admin_only(handler):
    @wraps(handler)
    async def wrapper(message_or_callback, *args, **kwargs):
        user_id = None
        if isinstance(message_or_callback, Message):
            user_id = message_or_callback.from_user.id
        elif isinstance(message_or_callback, CallbackQuery):
            user_id = message_or_callback.from_user.id

        if user_id not in ADMIN_IDS:
            if isinstance(message_or_callback, Message):
                await message_or_callback.answer("❌ Доступ запрещён. Только для админа.")
            elif isinstance(message_or_callback, CallbackQuery):
                await message_or_callback.answer("❌ Доступ запрещён. Только для админа.", show_alert=True)
            return
        return await handler(message_or_callback, *args, **kwargs)
    return wrapper


async def invoice_link(price: int, duration: int) -> str:
    logger.info(f"invoice_link, data: [price: {price}, duration: {duration}]")
    prices = [LabeledPrice(label='Подписка berezka VPN', amount=price)]
    sub_link = await bot.create_invoice_link(title="Подписка berezkaVPN", 
                            description=f'Подписка на {tariff_config.get_days(duration)}', 
                            payload=f"paid_tariff:{price}",
                            currency="XTR",
                            prices=prices,
                            is_flexible=False,
                            subscription_period=duration,
                            )
    return sub_link


async def create_payment_message(handler: CallbackQuery, tariff_id: str):
    await handler.answer()
    logger.info("create_payment_messge")
    tariff = tariff_config.tariffs[tariff_id]
    duration_days = tariff_config.get_days(tariff.duration_seconds)
    yookassa_qr_url, _ = create_payment_test(tariff.price_rub, handler.message.chat.id, tariff_id, "bank_card")
    # yookassa_card_url, _ = create_payment(tariff.price_rub, handler.message.chat.id)
    sub_link = await invoice_link(tariff.price_stars, tariff_config.MONTH)
    await handler.message.answer(text=f"<b>Вы выбрали тариф:</b> {tariff.name}\n"
                                      f"💰 Стоимость: {tariff.price_rub}₽ / {tariff.price_stars}⭐\n"
                                      f"📅 Срок действия: {duration_days} дней\n\n"
                                      f"Выберите способ оплаты:",
                                reply_markup=current_sub_tariff(sub_link, yookassa_qr_url),
                                parse_mode="HTML")


@router.message(CommandStart())
async def hello(message: Message):
    logger.info("command /start")
    fake_username = faker.domain_name(2)
    fake_username = fake_username.split(".")[1]
    username = message.from_user.username if message.from_user.username is not None else fake_username
    await sql_queries.create_user(username=username, tg_id=message.chat.id)
    await message.answer(f"Привет {username}.\nЭто бот для покупки подписки на впн", reply_markup=menu_keyboard())

    
@router.message(F.text == "Купить")
async def buy_tariff(message: Message, user_data: User):
    text_lines = ["Выберите тариф для покупки:\n"]

    # Перебираем все тарифы из конфигурации
    for tariff in tariff_config.tariffs.values():
        text_lines.append(
            f"{tariff.name}, "
            f"Цена: `{tariff.price_rub}` ₽ или "
            f"`{tariff.price_stars}` ⭐"
        )

    text = "\n".join(text_lines)

    await message.answer(
        text,
        reply_markup=sub_tariff(),
        parse_mode="MarkdownV2"
    )


@router.message(F.text == "Профиль")
async def profile(message: Message, user_data: User):
    try:
        api_user = await proxy.get_user(user_data.username)
        expire_str = (
        "Нет срока" if api_user.expire == None
        else f"🕒 Действует до: `{datetime.fromtimestamp(api_user.expire).strftime('%Y-%m-%d')}`"
        )
        await message.answer("Данные по вашей подписке:\n"
                            f"🕒 Действует до: `{expire_str}`\n"
                            "🌍 Сервер: 🇸🇪 Швеция\n"
                            "💾 Использовано трафика: \n"
                            "\n"
                            "🔗 Ваша реферальная ссылка:\n"
                            f"`{user_data.ref_url}`",
                            parse_mode="MarkdownV2")
    except:
        await message.answer("У вас еще нет подписки, нажмите на `Подключиться` для получения тестовой подписки", parse_mode="MarkdownV2")
    
@router.message(F.text == "Подключиться")
async def connect(message: Message, user_data: User):
    logger.info("connect user")
    logger.info(f"sub_url: {user_data.subscription_url}")
    if user_data.subscription_url == 'None':
        proxy_url = await proxy.create_user(user_data.username, expire=0, data_limit=100_000_000)
        await sql_queries.edit_user(user_data.telegram_chat_id, subscription_url=proxy_url)
    else:
        proxy_url = user_data.subscription_url
    await message.answer(f"Твоя ссылка для подлкючения к впн:\n{proxy_url}")

@router.callback_query(lambda call: call.data.startswith("sub:"))
async def tariff_info(call: CallbackQuery):
    logger.info(f"callback query: tariff_info")

    tariff_id = call.data.split(":")[-1]
    await create_payment_message(call, tariff_id)


# ======================================================== Админские штуки ======================================================== #




@admin_only
@router.message(Command("users"))
async def show_users(message: Message):
    users = await sql_queries.get_users()
    if not users:
        await message.answer("Пользователи не найдены.")
        return

    keyboard = create_users_keyboard(users, page=1)
    await message.answer("Список всех пользователей:", reply_markup=keyboard)


@admin_only
@router.callback_query(lambda call: call.data.startswith("user:"))
async def admin_profile_manage(call: CallbackQuery):
    await call.answer()
    user = await sql_queries.get_user(call.data.split(":")[-1])
    await call.message.answer(f"Управление профилем {user.username}", reply_markup=admin_manage_profile(call.data.split(":")[-1]))


@admin_only
@router.callback_query(lambda c: c.data and c.data.startswith("users_page:"))
async def users_page_callback(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    users = await sql_queries.get_all_users()
    keyboard = create_users_keyboard(users, page=page)
    await callback.message.edit_text("Список всех пользователей:", reply_markup=keyboard)
    await callback.answer()  # убирает «часики» в Telegram

@admin_only
@router.message(Command("test_middle_data"))
async def test(message: Message, user_data: User):
    # logger.info(f"middle_data: User, {user_data["user_data"]["username"]}")
    await message.answer(f"{user_data.username}")

@admin_only
@router.message(Command("connect"))
async def connect(message: Message, user_data):
    logger.info("connect user")
    data = await sql_queries.get_user(tg_id=message.chat.id)
    username = data.username
    proxy_url = await proxy.create_user(username, expire=0, data_limit=100_000_000)
    await message.answer(f"Твоя ссылка для подлкючения к впн:\n{proxy_url}")

@admin_only
@router.message(Command("edit_user"))
async def edit_user(message: Message, user_data):
    data = await sql_queries.get_user(tg_id=message.chat.id)
    username = data.username
    await proxy.edit_user(username, expire=0, data_limit=0)

@admin_only
@router.message(Command("delete_user"))
async def delete_user(message: Message, user_data):
    data = await sql_queries.get_user(tg_id=message.chat.id)
    username = data.username
    await sql_queries.delete_user(tg_id=message.chat.id)
    await proxy.delete_user(username)
    await message.answer(f"Пользователь {username}, был удален")