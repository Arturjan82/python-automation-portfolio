import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logic import Rule, check  # noqa: E402


def test_alert_fires_once_when_level_crossed():
    rule = Rule("BTCUSDT", above=100)
    assert check(rule, 99) == []
    assert len(check(rule, 101)) == 1
    assert check(rule, 105) == []  # цена всё ещё выше: без повторов


def test_alert_rearms_after_price_returns():
    rule = Rule("BTCUSDT", above=100)
    check(rule, 101)
    check(rule, 95)  # вернулась под уровень
    assert len(check(rule, 102)) == 1


def test_below_level():
    rule = Rule("ETHUSDT", below=50)
    assert check(rule, 60) == []
    msgs = check(rule, 49.5)
    assert len(msgs) == 1 and "ниже" in msgs[0]


def test_both_levels_independent():
    rule = Rule("X", above=100, below=50)
    assert len(check(rule, 120)) == 1
    assert len(check(rule, 40)) == 1


def test_from_dict_validation():
    assert Rule.from_dict({"symbol": "btcusdt", "above": 1}).symbol == "BTCUSDT"
    with pytest.raises(ValueError):
        Rule.from_dict({"symbol": "BTCUSDT"})
    with pytest.raises(ValueError):
        Rule.from_dict({"symbol": "BTCUSDT", "above": 10, "below": 20})
