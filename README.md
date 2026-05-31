Тесты на писанные на Python, а не Java потому что у Python скорость написания быстрее, легче изменение тестов, построения отчетов и графиков и простая интеграция.

 



## Структура проекта (Java микросервисы + Python тесты)

queuepulse/
├── docker-compose.yml
├── init.sql
├── README.md
├── docs/
│   ├── methodology.md
│   └── results.md
├── services/
│   ├── producer/
│   │   ├── Dockerfile
│   │   ├── pom.xml
│   │   └── src/main/java/com/queuepulse/producer/
│   │       ├── Application.java
│   │       ├── controller/OrderController.java
│   │       ├── service/RabbitMqService.java
│   │       └── dto/OrderDto.java
│   ├── consumer/
│   │   ├── Dockerfile
│   │   ├── pom.xml
│   │   └── src/main/java/com/queuepulse/consumer/
│   │       ├── Application.java
│   │       ├── listener/OrderListener.java
│   │       ├── service/DwhService.java
│   │       └── entity/OrderEntity.java
│   └── mock/
│       ├── Dockerfile
│       ├── pom.xml
│       └── src/main/java/com/queuepulse/mock/
│           └── PaymentMockController.java
├── scripts/
│   ├── load_test.py
│   ├── generate_data.py
│   ├── analyze_results.py
│   └── monitor.sh
├── load-tests/
│   ├── smoke-test.js
│   ├── load-test.js
│   ├── spike-test.js
│   └── stress-test.js
├── profiles/
│   ├── constant.yml
│   ├── ramp-up.yml
│   └── peak.yml
└── results/
    └── .gitkeep



# Методология нагрузочного тестирования QueuePulse

## Жизненный цикл проекта по нагрузке

### 1. Планирование
- Определение целей: обработка 1000 заказов/сек
- Выбор метрик: latency (p95 < 500ms), throughput (>50 RPS), error rate (<1%)
- Настройка окружения: Docker, PostgreSQL, RabbitMQ

### 2. Разработка
- Создание скриптов на Java и Python
- Настройка тестовых сценариев
- Разработка заглушек для внешних сервисов

### 3. Подготовка стенда
- Docker Compose для микросервисов
- Настройка сетей и volumes
- Инициализация БД

### 4. Запуск тестов
- Smoke test (проверка работоспособности)
- Load test (номинальная нагрузка)
- Spike test (пиковая нагрузка)
- Stress test (запредельная нагрузка)
- Soak test (длительная нагрузка)

### 5. Анализ результатов
- Сбор метрик из Prometheus/API
- Визуализация в Grafana
- Формирование отчета

### 6. Оптимизация
- Настройка пулов соединений
- Оптимизация запросов
- Масштабирование consumer

## Этапы нагрузочного тестирования

| Этап | Длительность | Цель | Метрики |
|------|--------------|------|---------|
| Smoke | 30 сек | Проверка доступности | Status 200 |
| Ramp-up | 2 мин | Плавный рост нагрузки | RPS growth |
| Peak | 5 мин | Максимальная нагрузка | P95 latency |
| Ramp-down | 1 мин | Снижение нагрузки | Error rate |
| Cooldown | 30 сек | Восстановление | Recovery time |

## Основные и дополнительные тесты

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

# Генерация 1000 заказов
python scripts/generate_data.py

# Запуск нагрузочного теста
python scripts/load_test.py

# Мониторинг
bash scripts/monitor.sh

