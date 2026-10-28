"""Память диалогов: последние N сообщений на каждого пользователя."""
from collections import defaultdict, deque


class ChatHistory:
    def __init__(self, max_messages: int = 20):
        self._max = max_messages
        self._data: dict[int, deque] = defaultdict(lambda: deque(maxlen=self._max))

    def add(self, user_id: int, role: str, content: str) -> None:
        self._data[user_id].append({"role": role, "content": content})

    def get(self, user_id: int) -> list[dict]:
        """Сообщения для API. История должна начинаться с сообщения пользователя,
        поэтому после обрезки старых сообщений убираем ведущие ответы ассистента."""
        messages = list(self._data[user_id])
        while messages and messages[0]["role"] != "user":
            messages.pop(0)
        return messages

    def drop_last(self, user_id: int) -> None:
        """Убрать последнее сообщение (например, если запрос к API не удался)."""
        if self._data[user_id]:
            self._data[user_id].pop()

    def reset(self, user_id: int) -> None:
        self._data.pop(user_id, None)
