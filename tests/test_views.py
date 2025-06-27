from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.views import main

test_transaction = [
    {
        "Дата операции": "31.12.2021 16:44:00",
        "Дата платежа": "31.12.2021",
        "Номер карты": "*7197",
        "Статус": "OK",
        "Сумма операции": -160.89,
        "Валюта операции": "RUB",
        "Сумма платежа": -160.89,
        "Кэшбэк": 0,
        "Категория": "Супермаркеты",
        "Описание": "Колхоз",
    },
    {
        "Дата операции": "31.12.2021 16:42:04",
        "Дата платежа": 0,
        "Номер карты": "*7197",
        "Статус": "OK",
        "Сумма операции": -64.0,
        "Валюта операции": "RUB",
        "Сумма платежа": -64.0,
        "Кэшбэк": 70,
        "Категория": "Ж/д билеты",
        "Описание": "Колхоз",
    },
]


@patch("src.views.external_api_stock")
@patch("src.views.external_api_currency")
def test_main(mock_currency: MagicMock, mock_stock: MagicMock) -> None:
    """Тестируем функцию, которая создает заданный JSON-ответ"""
    mock_currency.return_value = [{"currency": "USD", "rate": 103.12}, {"currency": "EUR", "rate": 106.22}]
    mock_stock.return_value = [{"stock": "AAPL", "price": 150.12}, {"stock": "AMZN", "price": 3173.18}]
    result = main(pd.DataFrame(test_transaction), "2021-12-31 14:00:00", "Добрый вечер")
    assert result == (
        "{\n"
        '    "greeting": "Добрый вечер",\n'
        '    "cards": [\n'
        "        {\n"
        '            "last_digits": "7197",\n'
        '            "total_spent": 224.89,\n'
        '            "cashback": 2.0\n'
        "        }\n"
        "    ],\n"
        '    "top_transactions": [\n'
        "        {\n"
        '            "date": "31.12.2021",\n'
        '            "amount": 160.89,\n'
        '            "category": "Супермаркеты",\n'
        '            "description": "Колхоз"\n'
        "        },\n"
        "        {\n"
        '            "date": "31.12.2021",\n'
        '            "amount": 64.0,\n'
        '            "category": "Ж/д билеты",\n'
        '            "description": "Колхоз"\n'
        "        }\n"
        "    ],\n"
        '    "currency_rates": [\n'
        "        {\n"
        '            "currency": "USD",\n'
        '            "rate": 103.12\n'
        "        },\n"
        "        {\n"
        '            "currency": "EUR",\n'
        '            "rate": 106.22\n'
        "        }\n"
        "    ],\n"
        '    "stock_prices": [\n'
        "        {\n"
        '            "stock": "AAPL",\n'
        '            "price": 150.12\n'
        "        },\n"
        "        {\n"
        '            "stock": "AMZN",\n'
        '            "price": 3173.18\n'
        "        }\n"
        "    ]\n"
        "}"
    )


@patch("src.views.external_api_stock")
@patch("src.views.external_api_currency")
def test_main_empty(mock_currency: MagicMock, mock_stock: MagicMock) -> None:
    """Тестируем работу функции, когда транзакций в заданный период не найдено"""
    mock_currency.return_value = [{"currency": "USD", "rate": 103.12}, {"currency": "EUR", "rate": 106.22}]
    mock_stock.return_value = [{"stock": "AAPL", "price": 150.12}, {"stock": "AMZN", "price": 3173.18}]
    result = main(pd.DataFrame(test_transaction), "2024-12-31 14:00:00", "Добрый вечер")
    assert result == (
        "{\n"
        '    "greeting": "Добрый вечер",\n'
        '    "cards": [],\n'
        '    "top_transactions": [],\n'
        '    "currency_rates": [\n'
        "        {\n"
        '            "currency": "USD",\n'
        '            "rate": 103.12\n'
        "        },\n"
        "        {\n"
        '            "currency": "EUR",\n'
        '            "rate": 106.22\n'
        "        }\n"
        "    ],\n"
        '    "stock_prices": [\n'
        "        {\n"
        '            "stock": "AAPL",\n'
        '            "price": 150.12\n'
        "        },\n"
        "        {\n"
        '            "stock": "AMZN",\n'
        '            "price": 3173.18\n'
        "        }\n"
        "    ]\n"
        "}"
    )


def test_main_invalid(test_transactions: List[Dict[str, Any]]) -> None:
    """Тестируем поведение функции, когда неверный формат даты - вызываем ошибку"""
    with pytest.raises(ValueError) as exc_info:
        main(pd.DataFrame(test_transactions), "2021.12.31 14:00:00", "Добрый вечер")
    assert str(exc_info.value) == "Неверный формат даты и времени. Используйте YYYY-MM-DD HH:MM:SS"
