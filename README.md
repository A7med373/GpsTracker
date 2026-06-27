# GF22 GPS Tracker Web Service

Веб-сервис для приема, хранения и отображения координат GPS-трекеров GF22. Проект принимает данные по HTTP, сохраняет их в базу данных и показывает точки на интерактивной карте.

## Возможности

- Прием координат от GPS-трекера через HTTP GET/POST.
- Хранение данных в SQLite для разработки или PostgreSQL для production.
- REST API для получения координат.
- Интерактивная карта на Leaflet.js.
- Фильтрация данных по IMEI.
- Ограничение количества отображаемых точек.
- Health check для проверки состояния сервиса и БД.
- Скрипты для добавления тестовых данных и деплоя.

## Стек

- Python
- Flask
- SQLAlchemy
- SQLite / PostgreSQL
- Leaflet.js
- Gunicorn
- Nginx

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Приложение будет доступно по адресу:

```text
http://localhost:5000
```

## Переменные окружения

По умолчанию используется SQLite:

```env
DATABASE_URL=sqlite:///tracker.db
PORT=5000
```

Для PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost/tracker_db
PORT=5000
```

## Основные endpoints

```text
GET  /                         - карта с треками
GET  /api/health               - проверка состояния приложения
GET  /api/locations            - список координат
GET  /update                   - прием координат от трекера
```

Пример отправки координат:

```bash
curl "http://localhost:5000/update?imei=861261027896790&lat=56.95&lng=24.11&ts=2025-05-21%2014:00:00"
```

## Тестовые данные

```bash
python add_sample_data.py --url http://localhost:5000
```

## Тесты

```bash
pytest
```

## Production-запуск

```bash
gunicorn -w 4 -b 0.0.0.0:80 app:app
```

Для production рекомендуется запускать приложение за Nginx и использовать PostgreSQL.

## Структура

```text
app.py              - Flask-приложение и API
templates/          - HTML-страницы
add_sample_data.py  - генератор тестовых координат
deploy.sh           - скрипт деплоя на сервер
test_tracker.py     - тесты
```
