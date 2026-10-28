# Telegram-ассистент на Claude API

Небольшой Telegram-бот, который отвечает на вопросы с помощью модели Claude (Anthropic) и помнит контекст диалога. Написан на Python (aiogram 3, anthropic SDK).

## Что умеет
- отвечает на текстовые сообщения, помнит последние N реплик каждого пользователя;
- команды `/start`, `/reset` (сбросить диалог), `/id` (показать свой Telegram ID);
- **доступ только для своих**: бот отвечает лишь пользователям из `ALLOWED_USER_IDS`, чтобы чужие запросы не тратили деньги на API;
- длинные ответы режутся на части под лимит Telegram (4096 символов);
- при ошибке API бот не падает и не портит историю диалога;
- запускается как сервис на Linux (пример unit-файла для systemd в `deploy/`).

## Запуск
```bash
python -m venv .venv
.venv\Scripts\activate          # Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # Linux: cp .env.example .env, затем впишите токены
python bot.py
```
1. Создайте бота у [@BotFather](https://t.me/BotFather), токен впишите в `TELEGRAM_TOKEN`.
2. Ключ API получите в консоли Anthropic, впишите в `ANTHROPIC_API_KEY`.
3. Запустите бота, отправьте ему `/id`, свой ID впишите в `ALLOWED_USER_IDS` и перезапустите.

## Тесты
```bash
pytest
```
Проверяются память диалогов (обрезка, изоляция пользователей, сброс) и разбиение длинных сообщений.

## Структура
| Файл | Назначение |
|---|---|
| `bot.py` | обработчики Telegram и вызов Claude API |
| `config.py` | настройки из переменных окружения |
| `history.py` | память диалогов |
| `textutils.py` | разбиение длинных ответов |
| `deploy/` | unit-файл systemd |

## Заметки
Секреты хранятся только в `.env` (он в `.gitignore`). Модель меняется переменной `CLAUDE_MODEL`.
