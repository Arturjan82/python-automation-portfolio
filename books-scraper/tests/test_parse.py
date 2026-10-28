import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scraper import Book, parse_price, parse_rating, parse_stock, summary  # noqa: E402


def test_parse_price():
    assert parse_price("£51.77") == 51.77
    assert parse_price("Â£7") == 7.0  # так цену иногда отдаёт сайт при неверной кодировке


def test_parse_price_error():
    with pytest.raises(ValueError):
        parse_price("бесплатно")


def test_parse_rating():
    assert parse_rating("star-rating Three") == 3
    assert parse_rating("star-rating Five") == 5
    assert parse_rating("star-rating") == 0


def test_parse_stock():
    assert parse_stock("\n In stock \n") is True
    assert parse_stock("Out of stock") is False


def test_summary_picks_cheapest_good_books_in_stock():
    books = [
        Book("A", 10.0, 5, True, "u1"),
        Book("B", 5.0, 3, True, "u2"),   # рейтинг ниже 4: не попадает
        Book("C", 7.0, 4, False, "u3"),  # нет в наличии: не попадает
        Book("D", 8.0, 4, True, "u4"),
    ]
    text = summary(books)
    assert "Книг собрано: 4" in text
    assert text.index("D") < text.index("A")
    assert "  B" not in text and "  C" not in text
