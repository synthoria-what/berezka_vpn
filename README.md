# Telegram VPN Bot

**Кратко:** бот для продажи VPN-услуг через Telegram. Поддерживает инвойсы (YooKassa), *Telegram Stars* для дополнительных покупок/баллов, реферальную систему, автоматическую генерацию конфигураций (WireGuard/OpenVPN), выбор страны сервера, уведомления об окончании подписки и простую панель админа.

---

## Фичи

* Покупка тарифов через YooKassa (Invoice / платежи в Telegram).
* Интеграция с *Telegram Stars* — возможность дарить *звёзды* или принимать их как частичную оплату.
* Автоматическая выдача конфигураций (WireGuard/OpenVPN) после оплаты.
* Тарифы: 1 мес, 3 мес, 12 мес + пробный день.
* Выбор сервера (страна), смена сервера пользователем.
* Уведомления: напоминание за 3 дня до окончания, автоматическое продление (опционально).
* Реферальная программа: пригласил — получил бесплатные дни/скидку.
* Поддержка 24/7 (чат с оператором или тикеты).
* Админ-команды для управления тарифами, пользователей и раздачи дней/баллов.
* Логи оплат и событий, статистика.

---

## Технологический стек

* Python + aiogram — Telegram bot framework.
* SQLAlchemy — ORM.
* PostgreSQL — СУБД.
* YooKassa — платежный шлюз.
* Telegram Stars — внутренняя микро-платежная система платформы (используется через Bot API).
* Redis — кеш/очереди/сессии (опционально).
* Docker / docker-compose — контейнеризация.

---

## Архитектура (вкратце)

1. **Bot** (aiogram) — принимает команды и inline-кнопки, отправляет инвойсы, обрабатывает webhook-уведомления.
2. **Worker** (async tasks) — генерация конфигов, отправка писем/файлов, фоновые напоминания.
3. **DB** (Postgres + SQLAlchemy) — хранение пользователей, подписок, транзакций, рефералов.
4. **YooKassa webhook** — подтверждает платежи и переводит подписку в активное состояние.
5. **Admin commands / dashboard** — управление тарифами, просмотр транзакций.

---

## Структура проекта (пример)

```
bot/
  ├─ handlers/
  │   ├─ start.py
  │   ├─ payments.py
  │   ├─ profile.py
  │   └─ admin.py
  ├─ services/
  │   ├─ payments.py
  │   ├─ config_generator.py
  │   └─ yookassa_client.py
  ├─ db/
  │   ├─ models.py
  │   ├─ crud.py
  │   └─ session.py
  ├─ keyboards.py
  ├─ config.py
  └─ main.py

worker/
  ├─ tasks.py
  └─ scheduler.py

migrations/ (alembic)
```

---

## Модели (основные сущности)

* **User**: id, telegram_id, username, language, referral_code, balance_stars, created_at.
* **Subscription**: id, user_id, plan_id, active_from, active_to, status, server_country.
* **Plan**: id, name, price_cents, period_days, description.
* **Transaction**: id, user_id, provider (yookassa/telegram_stars), provider_id, amount_cents, currency, status, meta.
* **Referral**: id, inviter_user_id, invited_user_id, reward_given.

---

## Установка (локально)

1. Клонировать репозиторий:

```bash
git clone git@github.com:you/vpn-telegram-bot.git
cd vpn-telegram-bot
```

2. Создать `.env` файл (пример ниже).
3. Запустить контейнеры (Postgres, Redis) и приложение через `docker-compose`.

---

## Пример `.env`

```
BOT_TOKEN=123456:ABC-DEF
ADMIN_IDS=123456789,987654321
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/vpn
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
WEBHOOK_HOST=https://your.domain
WEBHOOK_PATH=/webhook/yookassa
WEBHOOK_URL=${WEBHOOK_HOST}${WEBHOOK_PATH}
BASE_URL=https://your.domain
REDIS_URL=redis://redis:6379/0
JWT_SECRET=supersecret
ALLOW_TRIAL=true
TRIAL_DAYS=1

# Настройки генерации конфигов
WG_PRIVATE_KEY=... (или генерировать динамически)
WG_SERVER_ENDPOINT=wg.example.com:51820
```

---

## Yookassa интеграция (схема)

1. Пользователь выбирает тариф -> бот создаёт платёж (создаёт заказ в БД с `pending`).
2. Перенаправление на оплату — через API или Telegram Invoice.
3. YooKassa отправляет webhook о статусе платежа.
4. При успешном платеже: бот отмечает транзакцию `paid`, активирует/создаёт `Subscription`, генерирует конфиг и отсылает пользователю.
5. Логи и метрики сохраняются.

---

## Telegram Stars (идея использования)

* Пользователи могут отправлять *stars* боту (или канал/чат), использовать их как частичную оплату.
* Бот отслеживает сумму в `Transaction(provider='telegram_stars')`.
* Можно внедрить «скидку за звёзды» или давать дополнительные дни за определённое количество звёзд.

> Важно: API Telegram для Stars (если ограничено) нужно проверять — возможно потребуется ручная обработка донатов/платежей через channel payment settings.

---

## Примеры команд (для пользователя)

* `/start` — приветствие и главное меню.
* `Купить` — выбор тарифов.
* `/profile` — информация о подписке.
* `/servers` — список доступных серверов и смена.
* `support` — написать оператору.
* `trial` — активировать пробный день (если доступен).

## Admin команды

* `/admin/stats` — текущие показатели (активные подписки, доходы).
* `/admin/give_days {user_id} {days}` — выдать бесплатные дни.
* `/admin/refunds {txn_id}` — инициировать возврат (через YooKassa API).

---

## Примеры реализации (псевдо)

**Отправка инвойса (aiogram):**

```py
from aiogram import Bot
from aiogram.types import LabeledPrice

async def send_invoice(chat_id, title, description, amount_cents, payload):
    prices = [LabeledPrice(label=title, amount=amount_cents)]
    await bot.send_invoice(
        chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=YOOKASSA_TOKEN,
        currency="USD",
        prices=prices,
        start_parameter="vpn-subscribe"
    )
```

**Обработка webhook от YooKassa (псевдо):**

```py
# получать POST из yookassa -> проверить подпись -> обновить транзакцию -> активировать подписку
```

---

## Миграции

Рекомендуется использовать Alembic для миграций схемы БД. Добавьте `alembic` в проект и настройте `env.py` для asyncpg/SQLAlchemy.

---

## Безопасность

* Храните секреты в `.env` или в хранилище секретов (Vault).
* Шифруйте генерацию конфигов и не логируйте приватные ключи.
* Ограничьте доступ к админ-командам (только `ADMIN_IDS`).

---

## Деплой

* Используйте docker-compose / Kubernetes.
* Настройте HTTPS (Let's Encrypt) для вебхуков.
* Резервное копирование PostgreSQL.

---

## Contributing

Пулл-реквесты приветствуются. Пожалуйста, создавайте ветки feature/* и открывайте PR в `develop`.

---

## License

MIT
