from aiogram.fsm.state import State, StatesGroup

class WeatherStates(StatesGroup):
    """
    Сценарий:
    1) Пользователь вводит одну точку маршрута за раз (или '-')
    2) Если у города несколько вариантов, выбирает по кнопкам
    3) Повторяем, пока не '-' => завершаем ввод маршрутов
    4) Выбор дней прогноза
    5) Подтверждение
    """
    input_route = State()
    choose_variant = State()
    choose_days = State()
    confirm = State()
