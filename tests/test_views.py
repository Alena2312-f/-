import json
import os
from unittest.mock import MagicMock, patch

from src.views import main

def test_main_no_file():
    """Проверка поведения при отсутствии файла operations.xlsx"""
    # Переименуем файл, если он существует, чтобы симулировать отсутствие
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "operations.xlsx")
    temp_path = file_path + ".bak"

    file_exists = os.path.exists(file_path)
    if file_exists:
        os.rename(file_path, temp_path)

    try:
        result = main("2023-01-01 12:00:00")
        data = json.loads(result)
        assert "error" in data and "не найден" in data["error"], "Ошибка при отсутствии файла не обработана"
        print("test_main_no_file: PASSED")
    finally:
        # Восстановим файл
        if file_exists:
            os.rename(temp_path, file_path)

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

@patch("src.views.get_stock_data")
@patch("src.views.get_currency_rates")
def test_main_valid_date(mock_currency: MagicMock, mock_stock: MagicMock) -> None:
    """Тестируем функцию, которая создает заданный JSON-ответ"""
    mock_currency.return_value = [{"currency": "USD", "rate": 103.12}, {"currency": "EUR", "rate": 106.22}]
    mock_stock.return_value = [{"stock": "AAPL", "price": 150.12}, {"stock": "AMZN", "price": 3173.18}]
    result = main("2021-12-31 14:00:00")
    assert result == (
         '{\n'
         '  "greeting": "Добрый день",\n'
         '  "cards": [\n'
         '    {\n'
         '      "last_digits": "*5091",\n'
         '      "total_spent": -12743.99,\n'
         '      "cashback": -127.44\n'
         '    },\n'
         '    {\n'
         '      "last_digits": "nan",\n'
         '      "total_spent": 0.0,\n'
         '      "cashback": 0.0\n'
         '    },\n'
         '    {\n'
         '      "last_digits": "*7197",\n'
         '      "total_spent": -23240.8,\n'
         '      "cashback": -232.41\n'
         '    },\n'
         '    {\n'
         '      "last_digits": "*4556",\n'
         '      "total_spent": 198770.3,\n'
         '      "cashback": 1987.7\n'
         '    }\n'
         '  ],\n'
         '  "top_transactions": [\n'
         '    {\n'
         '      "date": "22.12.2021",\n'
         '      "amount": -28001.94,\n'
         '      "category": "Переводы",\n'
         '      "description": "Перевод Кредитная карта. ТП 10.2 RUR"\n'
         '    },\n'
         '    {\n'
         '      "date": "30.12.2021",\n'
         '      "amount": -20000.0,\n'
         '      "category": "Переводы",\n'
         '      "description": "Константин Л."\n'
         '    },\n'
         '    {\n'
         '      "date": "16.12.2021",\n'
         '      "amount": -14216.42,\n'
         '      "category": "ЖКХ",\n'
         '      "description": "ЖКУ Квартира"\n'
         '    },\n'
         '    {\n'
         '      "date": "23.12.2021",\n'
         '      "amount": -10000.0,\n'
         '      "category": "Переводы",\n'
         '      "description": "Светлана Т."\n'
         '    },\n'
         '    {\n'
         '      "date": "02.12.2021",\n'
         '      "amount": -5510.8,\n'
         '      "category": "Каршеринг",\n'
         '      "description": "Ситидрайв"\n'
         '    }\n'
         '  ],\n'
         '  "currency_rates": [\n'
         '    {\n'
         '      "currency": "USD",\n'
         '      "rate": 103.12\n'
         '    },\n'
         '    {\n'
         '      "currency": "EUR",\n'
         '      "rate": 106.22\n'
         '    }\n'
         '  ],\n'
         '  "stock_prices": [\n'
         '    {\n'
         '      "stock": "AAPL",\n'
         '      "price": 150.12\n'
         '    },\n'
         '    {\n'
         '      "stock": "AMZN",\n'
         '      "price": 3173.18\n'
         '    }\n'
         '  ]\n'
         '}')





def test_main_invalid_date():
    """Проверка поведения при невалидной дате"""
    result = main("invalid-date-format")
    data = json.loads(result)
    assert "error" in data, "Ошибка при невалидной дате не обработана"


