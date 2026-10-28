"""Telegram-ассистент на Claude API (aiogram 3 + anthropic)."""
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from anthropic import AsyncAnthropic

from config import Settings
from history import ChatHistory
from textutils import split_message

log = logging.getLogger("assistant")


def build_dispatcher(settings: Settings, client: AsyncAnthropic) -> Dispatcher:
    dp = Dispatcher()
    history = ChatHistory(settings.max_history)

    def allowed(message: Message) -> bool:
        return message.from_user is not None and message.from_user.id in settings.allowed_user_ids

    @dp.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer(
            "Привет! Я ассистент на базе Claude. Просто напишите вопрос.\n"
            "/reset - начать диалог заново\n/id - показать ваш Telegram ID"
        )

    @dp.message(Command("id"))
    async def show_id(message: Message) -> None:
        # Нужно владельцу, чтобы внести свой ID в ALLOWED_USER_IDS
        await message.answer(f"Ваш ID: {message.from_user.id}")

    @dp.message(Command("reset"))
    async def reset(message: Message) -> None:
        if allowed(message):
            history.reset(message.from_user.id)
            await message.answer("Диалог сброшен.")

    @dp.message(F.text)
    async def chat(message: Message) -> None:
        if not allowed(message):
            # Защита от чужих запросов: каждый ответ Claude стоит денег
            await message.answer("Доступ закрыт. Отправьте /id владельцу бота.")
            return
        uid = message.from_user.id
        history.add(uid, "user", message.text)
        await message.bot.send_chat_action(message.chat.id, "typing")
        try:
            response = await client.messages.create(
                model=settings.model,
                max_tokens=1024,
                system=settings.system_prompt,
                messages=history.get(uid),
            )
        except Exception:
            log.exception("Ошибка запроса к Claude API")
            history.drop_last(uid)  # чтобы роли в истории не нарушились
            await message.answer("Не получилось получить ответ. Попробуйте позже.")
            return
        answer = "".join(b.text for b in response.content if b.type == "text")
        history.add(uid, "assistant", answer)
        for part in split_message(answer):
            await message.answer(part)

    return dp


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = Settings.from_env()
    if not settings.allowed_user_ids:
        log.warning("ALLOWED_USER_IDS пуст: бот никому не ответит. Узнайте ID командой /id.")
    bot = Bot(settings.telegram_token)
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    dp = build_dispatcher(settings, client)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
