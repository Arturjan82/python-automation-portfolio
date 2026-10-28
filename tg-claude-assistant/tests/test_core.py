import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from history import ChatHistory  # noqa: E402
from textutils import split_message  # noqa: E402


def test_history_keeps_only_last_messages():
    h = ChatHistory(max_messages=4)
    for i in range(6):
        h.add(1, "user" if i % 2 == 0 else "assistant", str(i))
    contents = [m["content"] for m in h.get(1)]
    assert contents == ["2", "3", "4", "5"]
    assert h.get(1)[0]["role"] == "user"


def test_history_starts_with_user_after_trim():
    h = ChatHistory(max_messages=3)
    h.add(1, "user", "a")
    h.add(1, "assistant", "b")
    h.add(1, "user", "c")
    h.add(1, "assistant", "d")  # в deque остались b, c, d
    msgs = h.get(1)
    assert msgs[0]["role"] == "user"
    assert [m["content"] for m in msgs] == ["c", "d"]


def test_history_users_are_isolated_and_reset_works():
    h = ChatHistory()
    h.add(1, "user", "x")
    h.add(2, "user", "y")
    h.reset(1)
    assert h.get(1) == []
    assert h.get(2)[0]["content"] == "y"


def test_drop_last():
    h = ChatHistory()
    h.add(1, "user", "x")
    h.drop_last(1)
    assert h.get(1) == []


def test_split_message_short_and_empty():
    assert split_message("привет") == ["привет"]
    assert split_message("   ") == ["(пустой ответ)"]


def test_split_message_long_text_fits_limit_and_loses_nothing():
    text = "\n".join(f"строка {i}" for i in range(2000))
    parts = split_message(text, limit=500)
    assert all(len(p) <= 500 for p in parts)
    assert "".join(p.replace("\n", "") for p in parts).replace(" ", "") == text.replace("\n", "").replace(" ", "")
