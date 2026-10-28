"""Уведомления о цене криптовалют по публичному API Bybit (ключи не нужны).

Пример: python alert.py --rules rules.json --interval 60
Если заданы TELEGRAM_TOKEN и TELEGRAM_CHAT_ID, сигналы приходят в Telegram, иначе печатаются в консоль.
"""
import argparse
import json
import logging
import os
import time

import requests
from dotenv import load_dotenv

from logic import Rule, check

log = logging.getLogger("alert")
TICKER_URL = "https://api.bybit.com/v5/market/tickers"


def fetch_price(symbol: str) -> float:
    resp = requests.get(TICKER_URL, params={"category": "spot", "symbol": symbol}, timeout=10)
    resp.raise_for_status()
    items = resp.json()["result"]["list"]
    if not items:
        raise ValueError(f"Биржа не знает тикер {symbol}")
    return float(items[0]["lastPrice"])


def notify(text: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        print(text)
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        ).raise_for_status()
    except requests.RequestException:
        log.exception("Не удалось отправить сообщение в Telegram")
        print(text)  # сигнал не должен потеряться


def load_rules(path: str) -> list[Rule]:
    with open(path, encoding="utf-8") as f:
        return [Rule.from_dict(item) for item in json.load(f)]


def run_once(rules: list[Rule]) -> None:
    for rule in rules:
        try:
            price = fetch_price(rule.symbol)
        except (requests.RequestException, ValueError, KeyError):
            log.exception("Не удалось получить цену %s", rule.symbol)
            continue  # одна неудача не должна останавливать остальные проверки
        log.info("%s = %s", rule.symbol, price)
        for message in check(rule, price):
            notify(message)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    load_dotenv()
    parser = argparse.ArgumentParser(description="Сигналы о цене криптовалют")
    parser.add_argument("--rules", default="rules.json", help="файл с правилами (см. rules.example.json)")
    parser.add_argument("--interval", type=int, default=60, help="пауза между проверками, секунд")
    parser.add_argument("--once", action="store_true", help="проверить один раз и выйти")
    args = parser.parse_args()

    rules = load_rules(args.rules)
    while True:
        run_once(rules)
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
