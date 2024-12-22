from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from request_funcs import get_localoties, get_multiday_forecast
from keyboards import create_location_keyboard, create_days_keyboard, confirm_keyboard
from states import WeatherStates


router = Router()
router.api_key = None


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот прогноза погоды. Используйте /help для просмотра доступных команд.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "Доступные команды:\n"
        "/start - Приветствие\n"
        "/help - Список команд\n"
        "/weather - Запрос прогноза погоды"
    )
    await message.answer(text)


@router.message(Command("weather"))
async def cmd_weather(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(route_list=[], route_count=1)
    await message.answer("Введите 1 точку маршрута:")
    await state.set_state(WeatherStates.input_route)


@router.message(WeatherStates.input_route)
async def handle_input_route(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    route_count = data["route_count"]

    if text == '-':
        if route_count == 1:
            await message.answer("Нужна хотя бы 1 точка маршрута. Повторите ввод:")
            return
        await message.answer("Выберите, на сколько дней нужен прогноз:", reply_markup=create_days_keyboard())
        await state.set_state(WeatherStates.choose_days)
        return

    locs = get_localoties(router.api_key, text)
    if locs is None:
        await message.answer("Ошибка сети или API. Попробуйте снова:")
        return
    if not locs:
        await message.answer("Не найдено. Введите другой город или '-' для окончания:")
        return

    # Если всего 1 вариант — берём сразу
    if len(locs) == 1:
        country, region, city, key_ = locs[0]
        route_list = data["route_list"]
        route_list.append({"country": country, "region": region, "city": city, "key": key_})
        await state.update_data(route_list=route_list)

        route_count += 1
        await state.update_data(route_count=route_count)
        await message.answer(f"Вы выбрали: {city}, {region}, {country}\nВведите {route_count} точку маршрута (или '-' для окончания):")
        return
    else:
        await state.update_data(tmp_locs=locs)
        kb = create_location_keyboard(locs)
        await message.answer("Выберите нужный вариант:", reply_markup=kb)
        await state.set_state(WeatherStates.choose_variant)


@router.callback_query(WeatherStates.choose_variant, F.data.startswith("loc_"))
async def handle_choose_variant(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    locs = data.get("tmp_locs", [])
    route_count = data["route_count"]
    route_list = data["route_list"]

    index_str = callback.data.split("_")[1]
    try:
        index = int(index_str)
    except ValueError:
        await callback.answer("Ошибка индекса.")
        return

    if index < 0 or index >= len(locs):
        await callback.answer("Индекс за пределами.")
        return

    country, region, city, key_ = locs[index]
    route_list.append({"country": country, "region": region, "city": city, "key": key_})

    route_count += 1
    await state.update_data(route_list=route_list, route_count=route_count, tmp_locs=None)

    await callback.message.answer(f"Вы выбрали: {city}, {region}, {country}")
    await callback.message.answer(f"Введите {route_count} точку маршрута (или '-' для окончания):")

    await state.set_state(WeatherStates.input_route)
    await callback.answer()


@router.callback_query(WeatherStates.choose_variant)
async def wrong_choose_callback(callback: CallbackQuery):
    await callback.answer("Неверный выбор кнопки.")


@router.message(WeatherStates.choose_variant)
async def wrong_choose_message(message: Message):
    await message.answer("Пожалуйста, нажмите на кнопку с нужным вариантом или подождите вывода вариантов.")


@router.callback_query(WeatherStates.choose_days, F.data.startswith("days_"))
async def handle_choose_days(callback: CallbackQuery, state: FSMContext):
    days_str = callback.data.split("_")[1]
    try:
        days = int(days_str)
    except ValueError:
        days = 5

    await state.update_data(days=days)
    await callback.message.answer("Подтвердить запрос прогноза?", reply_markup=confirm_keyboard())
    await state.set_state(WeatherStates.confirm)
    await callback.answer()


@router.callback_query(WeatherStates.confirm, F.data.startswith("confirm_"))
async def handle_confirm(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm_yes":
        data = await state.get_data()
        days = data.get("days", 5)
        route_list = data.get("route_list", [])

        for route in route_list:
            city_name = route["city"]
            forecast = get_multiday_forecast(router.api_key, route["key"], days)
            if not forecast:
                await callback.message.answer(f"Нет прогноза для: {city_name}")
                continue

            lines = [f"Прогноз в {city_name}:"]
            for item in forecast:
                date_str = item["Date"].split("T")[0]
                temp = item["MeanTempC"]
                rain = item["RainProb"]
                wind = item["WindSpeedKmH"]
                lines.append(f"{date_str}: {temp}°C, дождь {rain}%, ветер {wind} км/ч")

            await callback.message.answer("\n".join(lines))

        await callback.message.answer("Прогноз завершён.")
        await state.clear()
    else:
        await callback.message.answer("Запрос отменён.")
        await state.clear()

    await callback.answer()


@router.callback_query(WeatherStates.confirm)
async def wrang_confirm_callback(callback: CallbackQuery):
    await callback.answer("Некорректный выбор.")


@router.message(WeatherStates.confirm)
async def wrang_confirm_message(message: Message):
    await message.answer("Пожалуйста, нажмите на кнопку подтверждения или отмены.")
