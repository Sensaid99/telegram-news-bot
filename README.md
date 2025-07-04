
# Crypto Market Bot

Telegram бот для анализа криптовалютного рынка с расширенной функциональностью.

## Возможности

### 💰 Криптовалюты
- Актуальные цены и объемы торгов
- On-chain метрики (комиссии, TVL, время транзакций)
- Информация о валидаторах и TPS
- Поддержка основных сетей (Bitcoin, Ethereum, BNB Chain, Solana, XRP, TRON, TON, SUI)
- Графики цен и индикаторов
- Уведомления об изменениях

### 📊 Рыночный анализ
- Обзор состояния рынка
- Тренды и корреляции
- Объемы торгов
- Рыночные настроения
- Краткие и информативные отчеты

### 🌍 Макроэкономика
- Важные новости и их влияние на рынок
- Экономический календарь
- Анализ макроэкономических показателей
- Прогнозы и рекомендации

### 📈 Технический анализ
- Профессиональные торговые сигналы
- Технические индикаторы (MACD, RSI, Bollinger Bands)
- Уровни поддержки и сопротивления
- Паттерны и формации

### 🐋 Отслеживание китов
- Мониторинг крупных транзакций
- Анализ движений по сетям
- Активность бирж
- Концентрация токенов
- Уведомления о крупных движениях

### 📅 Экономический календарь
- Важные экономические события
- Фильтрация по регионам и датам
- Оценка влияния на крипторынок
- Уведомления о предстоящих событиях

### ⚙️ Настройки
- Персонализация уведомлений
- Выбор валюты отображения
- Настройка часового пояса
- Фильтры и пороговые значения
- Тема интерфейса

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/crypto-market-bot.git
cd crypto-market-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и добавьте необходимые переменные окружения:
```env
# Telegram
BOT_TOKEN=your_bot_token
CHANNEL_ID=your_channel_id

# APIs
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_secret

# Blockchain APIs
ETHERSCAN_API_KEY=your_etherscan_key
BSCSCAN_API_KEY=your_bscscan_key
SOLSCAN_API_KEY=your_solscan_key
TRONGRID_API_KEY=your_trongrid_key

# Other Services
FOREX_FACTORY_API_KEY=your_forex_factory_key
CRYPTOPANIC_API_KEY=your_cryptopanic_key
```

5. Запустите миграции базы данных:
```bash
alembic upgrade head
```

6. Запустите бота:
```bash
python bot.py
```

## Использование

1. Найдите бота в Telegram: @your_bot_name
2. Нажмите "Start" для начала работы
3. Используйте меню для навигации по разделам
4. Настройте уведомления в разделе "Настройки"

## Команды

### Основные
- `/start` - Запуск бота
- `/help` - Помощь
- `/settings` - Настройки

### Криптовалюты
- `/p <символ>` - Цена монеты
- `/v <символ>` - Объем торгов
- `/c <символ>` - График
- `/i <символ>` - Информация

### Уведомления
- `/alert_price <символ> <цена>` - Уведомление о цене
- `/alert_volume <символ> <объем>` - Уведомление об объеме
- `/alert_whale <сеть> <сумма>` - Уведомление о ките
- `/alerts_list` - Список уведомлений
- `/alerts_clear` - Очистить уведомления

### Анализ
- `/market` - Рыночный анализ
- `/macro` - Макроэкономика
- `/ta <символ>` - Технический анализ
- `/whales <сеть>` - Активность китов

### Настройки
- `/currency <код>` - Изменить валюту
- `/timezone <зона>` - Изменить часовой пояс
- `/format <формат>` - Формат времени
- `/theme <тема>` - Сменить тему

## Разработка

### Структура проекта
```
crypto-market-bot/
├── bot.py                 # Основной файл бота
├── config.py             # Конфигурация
├── requirements.txt      # Зависимости
├── alembic/             # Миграции базы данных
├── handlers/            # Обработчики команд
│   ├── menu.py
│   ├── crypto.py
│   ├── market.py
│   ├── macro.py
│   ├── technical.py
│   ├── whales.py
│   ├── calendar.py
│   ├── settings.py
│   └── help.py
├── services/           # Сервисы для работы с API
│   ├── binance.py
│   ├── market_data.py
│   ├── blockchain_stats.py
│   ├── technical_analysis.py
│   ├── whale_tracker.py
│   ├── news_service.py
│   ├── macro_calendar.py
│   └── user_settings.py
└── database/          # Работа с базой данных
    ├── models.py
    └── session.py
```

### Добавление новой функциональности

1. Создайте новый обработчик в директории `handlers/`
2. Добавьте необходимые сервисы в `services/`
3. Обновите маршрутизацию в `bot.py`
4. Добавьте тесты в `tests/`
5. Обновите документацию

## Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функциональности
3. Внесите изменения
4. Отправьте pull request

## Лицензия

