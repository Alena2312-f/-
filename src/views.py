import json
import logging
import os
from datetime import datetime

import pandas as pd

from src.utils import (
    filter_transactions_by_month,
    get_card_data,
    get_currency_rates,
    get_greeting,
    get_stock_data,
    get_top_transactions,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main(datetime_str: str) -> str:
    """Главная функция для анализа транзакций и генерации JSON-ответа для главной страницы."""
    try:
        logging.info(f"Начало обработки данных для даты и времени: {datetime_str}")

        # 1. Загрузка данных
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "operations.xlsx")
        df = pd.read_excel(file_path)
        # file_path = os.path.join( "../data/operations.xlsx")
        # df = pd.read_excel(file_path)

        # 2. Преобразование столбцов с датами
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)

        # 3. Входящая дата и время
        input_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

        # 4. Фильтрация данных по дате
        filtered_df = filter_transactions_by_month(df, input_datetime)

        # 5. Загрузка настроек пользователя
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "user_settings.json")
        with open(file_path, "r") as f:
            user_settings = json.load(f)
        user_currencies = user_settings["user_currencies"]
        user_stocks = user_settings["user_stocks"]

        # 6. Получение данных о валютах и акциях
        currency_rates = get_currency_rates(user_currencies)
        stock_prices = get_stock_data(user_stocks)

        # 7. Генерация данных для главной страницы
        greeting = get_greeting(input_datetime.time())
        card_data = get_card_data(filtered_df)
        top_transactions = get_top_transactions(filtered_df)

        # 8. Формирование JSON-ответа
        response_data = {
            "greeting": greeting,
            "cards": card_data,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        logging.info("Данные успешно обработаны.")
        return json.dumps(response_data, indent=2, ensure_ascii=False, default=str)  # ensure_ascii=False для кириллицы
    except FileNotFoundError:
        logging.error("Файл operations.xlsx не найден.")
        return json.dumps({"error": "Файл operations.xlsx не найден"}, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}")
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)
