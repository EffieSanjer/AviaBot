from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F

from aviasales import get_airport, get_prices_for_dates
from keyboards.start import get_start_kb

router = Router()


@router.message(Command('start', 'restart'))
async def start(message: Message):
    await message.answer("Привет ✈", reply_markup=get_start_kb())


# States
class Direction(StatesGroup):
    origin = State()
    destination = State()
    departure_at = State()


@router.message(Command("cancel"))
@router.message(Text("Отмена", ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(Text("Новое направление"))
async def new_direction(message: Message, state: FSMContext):
    await message.answer("Введите аэропорт вылета (код из 3 букв, например: IKT или LED)")

    await state.set_state(Direction.origin)


@router.message(Direction.origin, F.text.func(lambda text: get_airport(text)))
async def origin_airport_chosen(message: Message, state: FSMContext):
    await state.update_data(origin=message.text)

    await message.answer("Введите аэропорт прилета (код из 3 букв, например: IKT или LED)")
    await state.set_state(Direction.destination)


@router.message(Direction.destination, F.text.func(lambda text: get_airport(text)))
async def destination_airport_chosen(message: Message, state: FSMContext):
    await state.update_data(destination=message.text)

    await message.answer("Введите дату вылета (в формате дд.мм.гггг)")
    await state.set_state(Direction.departure_at)


@router.message(Direction.origin)
@router.message(Direction.destination)
async def origin_airport_invalid(message: Message):
    await message.answer("Аэропорт не найден. Повторите ввод (код из 3 букв, например: IKT или LED)")


@router.message(Direction.departure_at, F.text.func(lambda message: datetime.strptime(message, '%d.%m.%Y')))
async def date_departure_chosen(message: Message, state: FSMContext):
    await state.update_data(departure_at=message.text)
    user_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Все верно",
                callback_data="get_air_tickets")
        ],
        [
            InlineKeyboardButton(
                text="Начать сначала",
                callback_data="new_direction")
        ],
    ])

    await message.answer(f"Аэропорт вылета: {user_data['origin']}\n"
                         f"Аэропорт прилета: {user_data['destination']}\n"
                         f"Дата вылета: {user_data['departure_at']}\n\n"
                         f"Все правильно?", reply_markup=keyboard)


@router.message(Direction.departure_at)
async def process_date_departure_invalid(message: Message):
    await message.answer("Неверный формат. Повторите ввод (в формате дд.мм.гггг)")


@router.callback_query(Text("get_air_tickets"), Direction.departure_at)
async def get_air_tickets(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_data['departure_at'] = datetime.strptime(user_data['departure_at'], '%d.%m.%Y').date()

    await callback.message.answer(get_prices_for_dates(user_data), reply_markup=get_start_kb())
    await callback.answer()


@router.callback_query(Text("new_direction"))
async def get_air_tickets(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.answer("Введите аэропорт вылета (код из 3 букв, например: IKT или LED)")
    await callback.answer()

    await state.set_state(Direction.origin)
