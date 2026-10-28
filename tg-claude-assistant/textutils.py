"""Вспомогательные функции для работы с текстом."""

TELEGRAM_LIMIT = 4096


def split_message(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    """Режет длинный ответ на части не длиннее лимита Telegram,
    стараясь делить по переводам строк, а не посреди слова."""
    text = text.strip()
    if not text:
        return ["(пустой ответ)"]
    parts: list[str] = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = text.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        parts.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    parts.append(text)
    return parts
