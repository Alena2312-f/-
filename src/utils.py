import json
import logging
import os
import urllib.request
from datetime import datetime, time

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY_CUR = os.getenv("API_KEY_CUR")

SP_500_API_KEY = os.getenv("SP_500_API_KEY")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_file_settings = os.path.join(base_dir, "data", "user_settings.json")
path_file_log = os.path.join(base_dir, "logs", "utils.log")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
greeting_logger = logging.getLogger("get_greeting")
get_card_data_logger = logging.getLogger("get_card_data")
get_top_transactions_logger = logging.getLogger("get_top_transactions")
get_currency_rates_logger = logging.getLogger("get_currency_rates")
get_stock_data_logger = logging.getLogger("get_stock_data")
filter_transactions_by_month_logger = logging.getLogger("filter_transactions_by_month")

with open(path_file_settings) as f:
    user_settings = json.load(f)
user_currencies = user_settings["user_currencies"]
user_stocks = user_settings["user_stocks"]


def get_greeting(current_time: time) -> str:
    """Определяет приветствие в зависимости от времени суток."""
    if 6 <= current_time.hour < 12:
        return "Доброе утро"
    elif 12 <= current_time.hour < 18:
        return "Добрый день"
    elif 18 <= current_time.hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_data(df: pd.DataFrame) -> list:
    """Получает данные по каждой карте: последние 4 цифры, общая сумма расходов, кешбэк."""
    card_data = []
    for card in df["Номер карты"].unique():
        card_df = df[df["Номер карты"] == card]
        total_spent = card_df["Сумма платежа"].sum()
        cashback = total_spent / 100
        card_data.append(
            {"last_digits": str(card), "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)}
        )
    return card_data


def get_top_transactions(df: pd.DataFrame) -> list:
    """Получает топ-5 транзакций по сумме платежа."""
    # Сортируем по возрастанию, так как большие отрицательные числа - это большие расходы
    top_transactions = df.sort_values(by="Сумма платежа", ascending=True).head(
        5
    )  # True для фортировки отрицательных значений, False для положительных
    return [
        {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": round(row["Сумма платежа"], 2),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for index, row in top_transactions.iterrows()
    ]


def get_currency_rates(currency: list) -> list[dict]:
    """Функция запроса курса валют"""
    get_currency_rates_logger.info("Начало работы функции (currency_rates)")
    api_key = API_KEY_CUR
    result = []
    for i in currency:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{i}"
        with urllib.request.urlopen(url) as response:
            body_json = response.read()
        body_dict = json.loads(body_json)
        result.append({"currency": i, "rate": round(body_dict["conversion_rates"]["RUB"], 2)})

    get_currency_rates_logger.info("Создание списка словарей для функции - get_currency_rates")

    get_currency_rates_logger.info("Окончание работы функции - get_currency_rates")
    return result


def get_stock_data(stocks: list) -> list:
    """Функция для получения данных об акциях из списка S&P500"""
    get_stock_data_logger.info("Начало работы функции (get_price_stock)")
    api_key = SP_500_API_KEY
    stock_prices = []
    get_stock_data_logger.info("Функция обрабатывает данные транзакций.")
    for stock in stocks:
        get_stock_data_logger.info("Перебор акций в списке 'stocks' в функции (get_price_stock)")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        response = requests.get(url, timeout=5, allow_redirects=False)
        result = response.json()

        stock_prices.append({"stock": stock, "price": round(float(result["Global Quote"]["05. price"]), 2)})
    get_stock_data_logger.info("Функция get_price_stock успешно завершила свою работу")
    return stock_prices


def filter_transactions_by_month(df: pd.DataFrame, date: datetime) -> pd.DataFrame:
    """
    Фильтрует DataFrame транзакций по диапазону дат (от начала месяца до указанной даты).

    Args:
        df: DataFrame с транзакциями.
        date: Дата, до которой нужно фильтровать транзакции.

    Returns:
        Отфильтрованный DataFrame.
    """
    start_of_month = date.replace(day=1)
    return df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= date)]
