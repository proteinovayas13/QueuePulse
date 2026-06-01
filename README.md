# QueuePulse - Data Warehouse Monitoring System
Комплексная система для мониторинга Data Warehouse в реальном времени. Проект демонстрирует работу микросервисной архитектуры с использованием Java, RabbitMQ, PostgreSQL и автоматизированным нагрузочным тестированием.

Настроен автоматический Telegram-бот для мониторинга Data Warehouse в реальном времени и полный цикл CI/CD с использованием GitHub Actions и GitHub Pages.

Дашборд отображает в реальном времени:
- Общее количество заказов
- Общую выручку
- Статус системы
- CPU Usage (Consumer, Producer, RabbitMQ)
- Message Rate (RPS через RabbitMQ)


### Основные
- Smoke test - базовая проверка
- Load test - номинальная нагрузка
- Stress test - запредельная нагрузка

### Дополнительные
- Spike test - резкий скачок нагрузки
- Soak test - длительная нагрузка
- Endurance test - проверка утечек памяти
- Chaos test - отказ компонентов

# QueuePulse - Load Testing Platform

## Требования
- Docker & Docker Compose
- Java 11+
- Python 3.9+
- Git

### Быстрый старт ###

```bash
# Клонирование
git clone https://github.com/your/queuepulse.git
cd queuepulse

# Запуск
docker-compose up -d

# Генерация тестовых данных (1000 заказов)
python scripts/generate_data.py

# Запуск нагрузочного теста
python scripts/load_test.py

# Запуск real-time дашборда
python scripts/live_monitor.py

# Отправка отчета в Telegram
python scripts/send_telegram_link.py

# Запуск нагрузочного теста
python scripts/load_test.py

# Мониторинг
bash scripts/monitor.sh

# Деплой происходит из папки /docs ветки main
source: /docs on branch main
