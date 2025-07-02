import os
from datetime import datetime, time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest
from dotenv import load_dotenv
from pandas import DataFrame

from src.utils import (
    filter_transactions_by_month,
    get_card_data,
    get_currency_rates,
    get_greeting,
    get_stock_data,
    get_top_transactions,
)

file_path = str(Path(__file__).resolve().parent.parent) + "\\data\\operations.xlsx"
load_dotenv()
API_KEY_CUR = os.getenv("API_KEY_CUR")


@pytest.mark.parametrize(
    "time_fixture, expected_greeting",
    [
        ("morning_time", "Доброе утро"),
        ("afternoon_time", "Добрый день"),
        ("evening_time", "Добрый вечер"),
        ("night_time", "Доброй ночи"),
    ],
)
def test_get_greeting_with_fixtures(time_fixture: str, expected_greeting: str, request: Any) -> None:
    """
    Тест функции get_greeting с использованием фикстур для времени.
    """
    current_time = request.getfixturevalue(time_fixture)  # Получаем значение фикстуры
    greeting = get_greeting(current_time)
    assert (
        greeting == expected_greeting
    ), f"Для времени {current_time} ожидалось приветствие '{expected_greeting}', но было получено '{greeting}'"


@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (6, "Доброе утро"),
        (11, "Доброе утро"),
        (12, "Добрый день"),
        (17, "Добрый день"),
        (18, "Добрый вечер"),
        (22, "Добрый вечер"),
        (23, "Доброй ночи"),
        (5, "Доброй ночи"),
        (0, "Доброй ночи"),
    ],
)
def test_get_greeting_with_hours(hour: int, expected_greeting: str) -> None:
    """
    Тест функции get_greeting с параметризацией по часу.
    """
    current_time = time(hour=hour, minute=0, second=0)
    greeting = get_greeting(current_time)
    assert (
        greeting == expected_greeting
    ), f"Для часа {hour} ожидалось приветствие '{expected_greeting}', но было получено '{greeting}'"


@patch("src.utils.time")
def test_get_greeting_mock_time(mock_time: MagicMock) -> None:
    """
    Тест функции get_greeting с использованием Mock для времени.
    """
    mock_time.return_value.hour = 10  # Устанавливаем час для мокированного времени
    greeting = get_greeting(mock_time.return_value)
    assert greeting == "Доброе утро"


# Тесты для get_card_data


def test_get_card_data_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Номер карты": [], "Сумма платежа": []})
    result = get_card_data(empty_df)
    assert result == [], "Для пустого DataFrame должен возвращаться пустой список"


def test_get_card_data_single_card(sample_dataframe: DataFrame) -> None:
    """
    Тест для случая, когда DataFrame содержит данные только по одной карте.
    """
    single_card_df = sample_dataframe[sample_dataframe["Номер карты"] == "*1234"]
    result = get_card_data(single_card_df)
    assert len(result) == 1, "Должна быть информация только по одной карте"
    assert result[0]["last_digits"] == "*1234", "Неверный номер карты"
    assert result[0]["total_spent"] == -125.0, "Неверная общая сумма расходов"
    assert result[0]["cashback"] == -1.25, "Неверный кешбэк"


def test_get_card_data_multiple_cards(sample_dataframe: DataFrame) -> None:
    """
    Тест для случая, когда DataFrame содержит данные по нескольким картам.
    """
    result = get_card_data(sample_dataframe)
    assert len(result) == 3, "Должна быть информация по трем картам"
    card_numbers = [card["last_digits"] for card in result]
    assert "*1234" in card_numbers, "Номер карты *1234 отсутствует"
    assert "*5678" in card_numbers, "Номер карты *5678 отсутствует"
    assert "*9012" in card_numbers, "Номер карты *9012 отсутствует"

    # Проверка сумм для карты *1234
    card_1234_data = next(card for card in result if card["last_digits"] == "*1234")
    assert card_1234_data["total_spent"] == -125.0, "Неверная общая сумма расходов для карты *1234"
    assert card_1234_data["cashback"] == -1.25, "Неверный кешбэк для карты *1234"


@pytest.mark.parametrize(
    "card_number, expected_total_spent, expected_cashback",
    [
        ("*1234", -125.0, -1.25),
        ("*5678", -60.0, -0.6),
        ("*9012", -75.0, -0.75),
    ],
)
def test_get_card_data_parameterized(
    sample_dataframe: DataFrame,
    card_number: str,
    expected_total_spent: float,
    expected_cashback: float,
) -> None:
    """
    Параметризованный тест для проверки данных по каждой карте.
    """
    result = get_card_data(sample_dataframe)
    card_data = next((card for card in result if card["last_digits"] == card_number), None)
    assert card_data is not None, f"Данные для карты {card_number} не найдены"
    assert card_data["total_spent"] == expected_total_spent, f"Неверная общая сумма расходов для карты {card_number}"
    assert card_data["cashback"] == expected_cashback, f"Неверный кешбэк для карты {card_number}"


# Тесты для get_top_transactions


def test_get_top_transactions_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": [], "Описание": []})
    result = get_top_transactions(empty_df)
    assert result == [], "Для пустого DataFrame должен возвращаться пустой список"


def test_get_top_transactions_less_than_5_transactions(sample_dataframe_top_transactions: pd.DataFrame) -> None:
    """
    Тест, когда в DataFrame меньше 5 транзакций.
    """
    df = sample_dataframe_top_transactions.sort_values(by="Сумма платежа", ascending=True).head(
        3
    )  # Сначала сортируем, потом берем 3 строки
    result = get_top_transactions(df)
    assert len(result) == 3, "Должно быть возвращено 3 транзакции"
    assert result[0]["amount"] == -800.00, "Неверная сортировка (первая транзакция)"
    assert result[1]["amount"] == -564.00, "Неверная сортировка (вторая транзакция)"
    assert result[2]["amount"] == -160.89, "Неверная сортировка (третья транзакция)"


def test_get_top_transactions_exactly_5_transactions(sample_dataframe_top_transactions: pd.DataFrame) -> None:
    """
    Тест, когда в DataFrame ровно 5 транзакций.
    """
    df = sample_dataframe_top_transactions.sort_values(by="Сумма платежа", ascending=True).head(5)
    result = get_top_transactions(df)
    assert len(result) == 5, "Должно быть возвращено 5 транзакций"
    assert result[0]["amount"] == -800.00, "Неверная сортировка (первая транзакция)"
    assert result[1]["amount"] == -564.00, "Неверная сортировка (вторая транзакция)"
    assert result[2]["amount"] == -160.89, "Неверная сортировка (третья транзакция)"
    assert result[3]["amount"] == -118.12, "Неверная сортировка (четвертая транзакция)"
    assert result[4]["amount"] == -78.05, "Неверная сортировка (пятая транзакция)"


def test_get_top_transactions_more_than_5_transactions(sample_dataframe_top_transactions: pd.DataFrame) -> None:
    """
    Тест, когда в DataFrame больше 5 транзакций.
    """
    df = sample_dataframe_top_transactions.sort_values(by="Сумма платежа", ascending=True)
    result = get_top_transactions(df)
    assert len(result) == 5, "Должно быть возвращено 5 транзакций"
    assert result[0]["amount"] == -800.00, "Неверная сортировка (первая транзакция)"
    assert result[1]["amount"] == -564.00, "Неверная сортировка (вторая транзакция)"
    assert result[2]["amount"] == -160.89, "Неверная сортировка (третья транзакция)"
    assert result[3]["amount"] == -118.12, "Неверная сортировка (четвертая транзакция)"
    assert result[4]["amount"] == -78.05, "Неверная сортировка (пятая транзакция)"


def test_get_top_transactions_date_format(sample_dataframe_top_transactions: pd.DataFrame) -> None:
    """
    Тест, что дата отформатирована правильно.
    """
    result = get_top_transactions(sample_dataframe_top_transactions)
    for transaction in result:
        assert isinstance(transaction["date"], str), "Дата должна быть строкой"
        assert len(transaction["date"]) == 10, "Длина строки даты должна быть 10 символов"
        assert transaction["date"][2] == ".", "Разделитель в дате должен быть точкой"
        assert transaction["date"][5] == ".", "Разделитель в дате должен быть точкой"


def test_filter_transactions_by_month_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": []})
    date = datetime(2024, 1, 15)
    result = filter_transactions_by_month(empty_df, date)
    assert result.empty, "Для пустого DataFrame должен возвращаться пустой DataFrame"


def test_filter_transactions_by_month_single_month(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест для фильтрации транзакций в пределах одного месяца.
    """
    date = datetime(2024, 1, 15)
    result = filter_transactions_by_month(sample_dataframe_by_month, date)
    assert len(result) == 2, "Должно быть возвращено 2 транзакции"
    assert (result["Дата операции"] <= date).all(), "Все даты должны быть до указанной даты"
    assert (result["Дата операции"] >= datetime(2024, 1, 1)).all(), "Все даты должны быть в январе"


def test_filter_transactions_by_month_same_date_as_transaction(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест, когда указанная дата совпадает с датой одной из транзакций.
    """
    date = datetime(2024, 1, 20)
    result = filter_transactions_by_month(sample_dataframe_by_month, date)
    assert len(result) == 3, "Должно быть возвращено 3 транзакции"
    assert date in result["Дата операции"].tolist(), "Должна быть транзакция за 20 января"


def test_filter_transactions_by_month_date_at_start_of_month(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест, когда указана дата в начале месяца.
    """
    date = datetime(2024, 1, 1)
    result = filter_transactions_by_month(sample_dataframe_by_month, date)
    assert len(result) == 0, "Должно быть возвращено 0 транзакций, так как ни одна дата меньше 1 января"


def test_filter_transactions_by_month_date_at_end_of_month(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест, когда указана дата в конце месяца.
    """
    date = datetime(2024, 1, 31)  # Предполагаем, что в sample_dataframe нет данных за январь
    result = filter_transactions_by_month(sample_dataframe_by_month, date)
    assert len(result) == 3, "Должно быть возвращено 3 транзакции (январь)"
    assert (result["Дата операции"] <= date).all(), "Все даты должны быть до указанной даты"
    assert (result["Дата операции"] >= datetime(2024, 1, 1)).any(), "Должна быть хотя бы одна дата в январе"


@patch("requests.get")
def test_currency_rates(mock_get):
    """Тестирование функции вывода курса валют"""
    mock_response_usd = Mock()
    mock_response_usd.json.return_value = {"conversion_rates": {"RUB": 78.48}}
    mock_response_eur = Mock()
    mock_response_eur.json.return_value = {"conversion_rates": {"RUB": 92.66}}
    mock_get.side_effect = [mock_response_usd, mock_response_eur]

    result = get_currency_rates(["USD", "EUR"])
    expected = [{"currency": "USD", "rate": 78.48}, {"currency": "EUR", "rate": 92.66}]
    assert result == expected


@patch("requests.get")
def test_fetch_stock_prices(mock_get):
    """Тестирование функции получения данных об акциях из списка S&P500"""

    mock_get.return_value.json.return_value = {"Global Quote": {"05. price": 203.92}}

    list_stocks = ["AAPL"]

    result = get_stock_data(list_stocks)
    expected = [
        {"stock": "AAPL", "price": 203.92},
    ]
    assert result == expected
