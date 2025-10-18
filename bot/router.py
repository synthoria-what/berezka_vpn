from ctypes import LibraryLoader
from re import L
from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, LabeledPrice, CallbackQuery
from keyboards import current_sub_rate, menu_keyboard, sub_rate
from config import config, SubPriceRub, SubPriceStars, SubDuration
from logger import Logger


logger = Logger.getinstance()
router = Router()
bot = Bot(config.tg_token)
sub_stars = SubPriceStars()
sub_rub = SubPriceRub()
sub_duration = SubDuration()


async def invoice_link(price: int, duration: int) -> str:
    logger.info(f"invoice_link, data: [price: {price}, duration: {duration}]")
    prices = [LabeledPrice(label='Подписка berezka VPN', amount=price)]
    sub_link = await bot.create_invoice_link(title="Подписка berezkaVPN", 
                            description=f'Подписка на {sub_duration.convert_to_days(duration)}', 
                            payload=f"paid_sub:{price}",
                            currency="XTR",
                            prices=prices,
                            is_flexible=False,
                            subscription_period=duration,
                            )
    return sub_link


@router.message(CommandStart())
async def hello(message: Message):
    logger.info("command /start")
    await message.answer(f"Привет, {message.from_user.first_name}.\nЭто бот для покупки подписки на впн", reply_markup=menu_keyboard())


@router.message(F.text == "Купить")
async def buy_sub(message: Message):
    logger.info('reply-button "Купить"')
    await message.answer("Выберите тариф для покупки:\n" \
                        f"- 1 месяц, Цена: {sub_rub.first_sub} рублей | {sub_stars.first_sub} ⭐\n" \
                        f"- 3 месяца, Цена: {sub_rub.second_sub} рублей | {sub_stars.second_sub} ⭐\n" \
                        f"- 6 месяцев, Цена: {sub_rub.third_sub} рублей | {sub_stars.third_sub} ⭐\n" \
                        f"- 12 месяцев, Цена: {sub_rub.fourth_sub} рублей | {sub_stars.fourth_sub} ⭐\n", reply_markup=sub_rate())


@router.callback_query(F.data == "first_rate")
async def first_sub_sub(call: CallbackQuery):
    logger.info(f'callback-query: {call.data}')
    sub_link = await invoice_link(sub_stars.first_sub, sub_duration.month)
    await call.message.answer("Выберите нужный вам способ оплаты:", 
                              reply_markup=current_sub_rate(sub_link, price=sub_rub.first_sub))


@router.callback_query(F.data == "second_rate")
async def second_sub_sub(call: CallbackQuery):
    logger.info(f'callback-query: {call.data}')
    await call.answer()
    await call.message.answer(f"Подписка: {call.data}")
    sub_link = await invoice_link(sub_stars.second_sub, sub_duration.month)
    await call.message.answer("Выберите нужный вам способ оплаты:", 
                              reply_markup=current_sub_rate(sub_link, price=sub_rub.second_sub))


@router.callback_query(F.data == "third_rate")
async def third_sub_sub(call: CallbackQuery):
    logger.info(f'callback-query: {call.data}')
    await call.answer()
    await call.message.answer(f"Подписка: {call.data}")
    sub_link = await invoice_link(sub_stars.third_sub, sub_duration.month)
    await call.message.answer("Выберите нужный вам способ оплаты:", 
                              reply_markup=current_sub_rate(sub_link, price=sub_rub.third_sub))


@router.callback_query(F.data == "fourth_rate")
async def fourth_sub_sub(call: CallbackQuery):
    logger.info(f'callback-query: {call.data}')
    await call.answer()
    await call.message.answer(f"Подписка: {call.data}")
    sub_link = await invoice_link(sub_stars.fourth_sub, sub_duration.month)
    await call.message.answer("Выберите нужный вам способ оплаты:",
                              reply_markup=current_sub_rate(sub_link, price=sub_rub.fourth_sub))