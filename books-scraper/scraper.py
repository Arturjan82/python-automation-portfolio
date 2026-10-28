"""Сбор каталога книг с учебного сайта books.toscrape.com через Playwright.

Пример: python scraper.py --pages 3 --out books.csv
"""
import argparse
import csv
import re
import statistics
from dataclasses import asdict, dataclass

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

BASE = "https://books.toscrape.com/catalogue/"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


@dataclass
class Book:
    title: str
    price: float
    rating: int
    in_stock: bool
    url: str


def parse_price(text: str) -> float:
    """'£51.77' -> 51.77"""
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        raise ValueError(f"Не удалось разобрать цену: {text!r}")
    return float(match.group())


def parse_rating(class_attr: str) -> int:
    """'star-rating Three' -> 3 (0, если рейтинг не найден)"""
    for word in class_attr.split():
        if word in RATINGS:
            return RATINGS[word]
    return 0


def parse_stock(text: str) -> bool:
    return "in stock" in text.lower()


def scrape_page(page, number: int) -> list[Book]:
    page.goto(f"{BASE}page-{number}.html", timeout=30_000)
    try:
        page.wait_for_selector("article.product_pod", timeout=10_000)
    except PlaywrightTimeout:
        return []  # страницы закончились
    books = []
    for card in page.query_selector_all("article.product_pod"):
        link = card.query_selector("h3 a")
        books.append(
            Book(
                title=link.get_attribute("title"),
                price=parse_price(card.query_selector("p.price_color").inner_text()),
                rating=parse_rating(card.query_selector("p.star-rating").get_attribute("class")),
                in_stock=parse_stock(card.query_selector("p.availability").inner_text()),
                url=BASE + link.get_attribute("href"),
            )
        )
    return books


def save_csv(books: list[Book], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig: чтобы Excel видел кириллицу и символы
        writer = csv.DictWriter(f, fieldnames=list(asdict(books[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(b) for b in books)


def summary(books: list[Book]) -> str:
    prices = [b.price for b in books]
    best = sorted((b for b in books if b.rating >= 4 and b.in_stock), key=lambda b: b.price)[:5]
    lines = [
        f"Книг собрано: {len(books)}",
        f"Средняя цена: £{statistics.mean(prices):.2f}, медиана: £{statistics.median(prices):.2f}",
        "5 самых дешёвых книг с рейтингом 4-5, которые есть в наличии:",
    ]
    lines += [f"  £{b.price:.2f}  {'*' * b.rating:<5}  {b.title}" for b in best]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Сбор каталога книг в CSV")
    parser.add_argument("--pages", type=int, default=3, help="сколько страниц каталога собрать (на сайте их 50)")
    parser.add_argument("--out", default="books.csv", help="файл для результата")
    args = parser.parse_args()

    books: list[Book] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for number in range(1, args.pages + 1):
            found = scrape_page(page, number)
            if not found:
                break
            books += found
            print(f"страница {number}: {len(found)} книг")
        browser.close()

    if not books:
        raise SystemExit("Ничего не собрано")
    save_csv(books, args.out)
    print(summary(books))
    print(f"Сохранено в {args.out}")


if __name__ == "__main__":
    main()
