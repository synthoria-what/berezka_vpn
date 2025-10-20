from ast import Call
from ctypes import LibraryLoader
from re import L
from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, LabeledPrice, CallbackQuery
from keyboards import current_sub_tariff, current_sub_tariff, menu_keyboard, sub_tariff
from config import config, TariffConfig
from logger import Logger
from payments import create_payment
from proxy_client import ProxyClient


logger = Logger.getinstance()
router = Router()
bot = Bot(config.tg_token)
tariff_config = TariffConfig()
proxy = ProxyClient()


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
    logger.info(f'callback-query: {handler.data} chat_id: {handler.message.chat.id}')
    tariff = tariff_config.tariffs[tariff_id]
    logger.info(f"tariff: id:{tariff_id}")
    duration_days = tariff_config.get_days(tariff.duration_seconds)
    yookassa_qr_url, _ = create_payment(tariff.price_rub, handler.message.chat.id, "sbp")
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
    await message.answer(f"Привет, {message.from_user.first_name}.\nЭто бот для покупки подписки на впн", reply_markup=menu_keyboard())


@router.message(Command("/admin"))
async def get_users(message: Message):
    logger.info("get_users_proxy")
    users = await proxy.get_users()
    print(users)


@router.message(F.text == "Купить")
async def buy_tariff(message: Message):
    logger.info('reply-button "Купить"')

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


@router.callback_query(lambda call: call.data.startswith("sub:"))
async def tariff_info(call: CallbackQuery):
    logger.info(f"callback query: tariff_info, data: {call.data}")

    tariff_id = call.data.split(":")[-1]
    await create_payment_message(call, tariff_id)