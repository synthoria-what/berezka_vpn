from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, LabeledPrice, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
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


ADMIN_IDS = config.admins_ids


class SendMessage(StatesGroup):
    message = State()

# ======================================================== Логика ======================================================== #


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
    username = handler.from_user.username
    proxy_user = await proxy.get_user(username)
    logger.warning(f"{proxy_user}")
    yookassa_qr_url, _ = create_payment_test(tariff.price_rub, 
                                             chat_id=handler.message.chat.id, 
                                             tariff_id=tariff_id,
                                             username=username,
                                             expire=proxy_user.expire)
    # yookassa_card_url, _ = create_payment(tariff.price_rub, handler.message.chat.id)
    sub_link = await invoice_link(tariff.price_stars, tariff_config.get_subscription_config(tariff_id)["expire"])
    await handler.message.answer(text=f"<b>Вы выбрали тариф:</b> {tariff.name}\n"
                                      f"💰 Стоимость: {tariff.price_rub}₽ / {tariff.price_stars}⭐\n"
                                      f"📅 Срок действия: {tariff_config.get_days(tariff.duration)} дней\n\n"
                                      f"Выберите способ оплаты:",
                                reply_markup=current_sub_tariff(sub_link, yookassa_qr_url),
                                parse_mode="HTML")


# ======================================================== Роуты бота ======================================================== # 


@router.message(CommandStart())
async def hello(message: Message):
    logger.info("command /start")
    check_ref_url = message.text.split(" ")
    if len(check_ref_url) > 1 and message.chat.id != int(check_ref_url[-1]):
        logger.warning("Пользователь перешел по реферальной ссылке")
        logger.info(f"ref_id={check_ref_url[-1]}")
        ref_user = await sql_queries.get_user(check_ref_url[-1])
        if ref_user:
            print(ref_user.users_invited)
            user = await sql_queries.edit_user(int(check_ref_url[-1]), users_invited=ref_user.users_invited + 1)
            logger.info(f"user-data: {user.users_invited}")
    fake_username = faker.domain_name(2)
    fake_username = fake_username.split(".")[1]
    username = message.from_user.username if message.from_user.username is not None else fake_username
    await sql_queries.create_user(username=username, tg_id=message.chat.id)
    user = await sql_queries.get_user(message.chat.id)
    if user.telegram_chat_id in ADMIN_IDS:
        await sql_queries.edit_user(message.chat.id, role="admin")
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
    api_user = await proxy.get_user(user_data.username)
    expire_str = (
    "Нет срока" if api_user.expire == None
    else f"{datetime.fromtimestamp(api_user.expire).strftime('%Y-%m-%d')}"
    )
    
    # Формируем клавиатуру только если пользователь админ
    keyboard = None
    if user_data.role == "admin":  # или проверка через ADMINS_IDS
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Открыть админ-панель", callback_data="open_admin_panel")]
            ]
        )
    
    await message.answer("Данные по вашей подписке:\n"
                        f"🕒 Действует до: `{expire_str}`\n"
                        "🌍 Сервер: Хельсинки\n"
                       f"💾 Использовано трафика: {api_user.used_traffic}\n"
                        "\n"
                        "🔗 Ваша реферальная ссылка:\n"
                        f"`https://t.me/test_invite_send_bot?start={message.chat.id}`\n"
                        f"Пользователей пригалашено: {user_data.users_invited}",
                        parse_mode="MarkdownV2", reply_markup=keyboard)
    
@router.message(F.text == "Подключиться")
async def connect(message: Message, user_data):
    logger.info("connect user")
    logger.info(f"sub_url: {user_data.subscription_url}")
    try:
        proxy_user = await proxy.get_user(user_data.username)
        proxy_url = proxy_user.subscription_url
        await sql_queries.edit_user(message.chat.id, subscription_url=proxy_url)
    except:
        if user_data.subscription_url == 'None':
            proxy_url = await proxy.create_user(user_data.username, expire=0, data_limit=100_000_000)
            await sql_queries.edit_user(user_data.telegram_chat_id, subscription_url=proxy_url)
        else:
            proxy_url = user_data.subscription_url
    await message.answer(f"Твоя ссылка для подлкючения к впн:\n{proxy_url}")

@router.callback_query(lambda call: call.data.startswith("sub:"))
async def tariff_info(call: CallbackQuery):
    logger.info(f"callback query: tariff_info, {call.data}")
    try:
        tariff_id = call.data.split(":")[-1]
        await create_payment_message(call, tariff_id)
    except Exception as ex:
        logger.error(f"Произошла ошибка при создании оплаты: {ex}")

# ======================================================== Админские штуки ======================================================== #


@router.message(Command("admin"))
@admin_only
async def admin_menu(message: Message):
    await message.answer(f"Здравствйте {message.from_user.username}",reply_markup=admin_menu_keyboard())
    

@router.callback_query(F.data == "admin_profile")
@admin_only
async def admin_profile(call: CallbackQuery, user_data):
    api_user = await proxy.get_user(user_data.username)
    expire_str = (
    "Нет срока" if api_user.expire == None
    else f"{datetime.fromtimestamp(api_user.expire).strftime('%Y-%m-%d')}"
    )
    await call.message.answer("Данные по вашей подписке:\n"
                        f"🕒 Действует до: `{expire_str}`\n"
                        "🌍 Сервер: Хельсинки\n"
                       f"💾 Использовано трафика: {api_user.used_traffic}\n"
                        "\n"
                        "🔗 Ваша реферальная ссылка:\n"
                        f"`https://t.me/test_invite_send_bot?start={call.message.chat.id}`\n"
                        f"Пользователей пригалашено: {user_data.users_invited}",
                        parse_mode="MarkdownV2")
    
@router.callback_query(F.data == "manager_users")
@admin_only
async def show_users(call: CallbackQuery):
    users = await sql_queries.get_users()
    if not users:
        await call.message.answer("Пользователи не найдены.")
        return

    keyboard = create_users_keyboard(users, page=1)
    await call.message.answer("Список всех пользователей:", reply_markup=keyboard)


@router.callback_query(F.data == "send_message_all")
@admin_only
async def send_message_all(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Напишите сообщение которое хотите отправить всем пользователям")
    await state.set_data({"message": call.message.text})
    await state.set_state(SendMessage.message)
    

@router.message(SendMessage.message)
async def send_message_all_confirm(message: Message, state: FSMContext):
    data = state.get_data()
    await message.answer(f"data: {data}")

@router.callback_query(lambda call: call.data.startswith("user:"))
@admin_only
async def admin_profile_manage(call: CallbackQuery):
    await call.answer()
    user = await sql_queries.get_user(call.data.split(":")[-1])
    await call.message.answer(f"Управление профилем {user.username}", reply_markup=admin_manage_profile(call.data.split(":")[-1]))


@router.callback_query(lambda c: c.data and c.data.startswith("users_page:"))
@admin_only
async def users_page_callback(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    users = await sql_queries.get_all_users()
    keyboard = create_users_keyboard(users, page=page)
    await callback.message.edit_text("Список всех пользователей:", reply_markup=keyboard)
    await callback.answer()  # убирает «часики» в Telegram


@router.callback_query(lambda call: call.data.startswith("del_user:"))
@admin_only
async def delete_user(call: CallbackQuery):
    await call.answer()
    chat_id = call.data.split(":")[-1]
    data = await sql_queries.get_user(tg_id=chat_id)
    username = data.username
    await sql_queries.delete_user(tg_id=chat_id)
    await proxy.delete_user(username)
    await call.message.answer(f"Профиль {username}, был удален")