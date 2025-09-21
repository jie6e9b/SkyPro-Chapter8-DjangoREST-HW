
# API Документация

## 1️⃣ Курсы (`CourseViewSet`)

| Метод | URL | Описание | Query Params |
|-------|-----|----------|--------------|
| GET | `/api/courses/` | Получить список всех курсов | `search=<text>` (по имени), `ordering=<field>` (по имени) |
| POST | `/api/courses/` | Создать новый курс | — |
| GET | `/api/courses/<id>/` | Получить информацию о курсе | — |
| PUT | `/api/courses/<id>/` | Полное обновление курса | — |
| PATCH | `/api/courses/<id>/` | Частичное обновление курса | — |
| DELETE | `/api/courses/<id>/` | Удалить курс | — |

**Пример запроса:**
```http
GET /api/courses/?search=Python&ordering=name
```

**Пример ответа:**
```json
[
    {
        "id": 1,
        "name": "Python для начинающих",
        "preview": null,
        "description": "Базовый курс по Python",
        "lessons_count": 2,
        "lessons_group": [
            {"name": "Введение в Python"},
            {"name": "Циклы и условия"}
        ]
    }
]
```

---

## 2️⃣ Уроки (`LessonViewSet`)

| Метод | URL | Описание | Query Params |
|-------|-----|----------|--------------|
| GET | `/api/lessons/` | Получить список всех уроков | `course=<id>` (по курсу), `search=<text>` (по имени), `ordering=<field>` |
| POST | `/api/lessons/` | Создать новый урок | — |
| GET | `/api/lessons/<id>/` | Получить информацию о уроке | — |
| PUT | `/api/lessons/<id>/` | Полное обновление урока | — |
| PATCH | `/api/lessons/<id>/` | Частичное обновление урока | — |
| DELETE | `/api/lessons/<id>/` | Удалить урок | — |

**Пример запроса:**
```
GET /api/lessons/?course=1&ordering=name
```

**Пример ответа:**
```json
[
    {
        "id": 1,
        "course": 1,
        "name": "Введение в Python",
        "description": "",
        "preview": null,
        "video_url": ""
    }
]
```

---

## 3️⃣ Платежи (`PaymentViewSet`)

| Метод | URL | Описание | Query Params |
|-------|-----|----------|--------------|
| GET | `/api/payments/` | Получить список всех платежей | `course`, `lesson`, `payment_type`, `user`, `search`, `ordering` |
| POST | `/api/payments/` | Создать новый платёж | — |
| GET | `/api/payments/<id>/` | Получить информацию о платеже | — |
| PUT | `/api/payments/<id>/` | Полное обновление платежа | — |
| PATCH | `/api/payments/<id>/` | Частичное обновление платежа | — |
| DELETE | `/api/payments/<id>/` | Удалить платёж | — |

**Пример запроса:**
```
GET /api/payments/?course=1&payment_type=cash&ordering=-payment_date
```

**Пример ответа:**
```json
[
    {
        "id": 1,
        "user": 1,
        "course": 1,
        "lesson": null,
        "payment_type": "cash",
        "payment_price": "1500.00",
        "payment_date": "2025-09-20T10:00:00Z"
    }
]
```

---

## 4️⃣ Пользователи (`UserUpdateAPIView`)

| Метод | URL | Описание |
|-------|-----|----------|
| PATCH | `/api/users/<id>/` | Частичное обновление данных пользователя (email, имя и т.д.) |

**Пример запроса:**
```json
{
    "email": "ivan_new@example.com",
    "first_name": "Иван"
}
```

**Пример ответа:**
```json
{
    "id": 1,
    "username": "ivan",
    "email": "ivan_new@example.com",
    "first_name": "Иван",
    "last_name": "",
    "is_active": true
}
```

---

## 5️⃣ Query Params и фильтры

| Эндпоинт | Параметр | Тип / Значение | Описание | Пример |
|-----------|----------|----------------|----------|--------|
| `/api/courses/` | `search` | строка | Поиск курса по имени | `/api/courses/?search=Python` |
| `/api/courses/` | `ordering` | `name` | Сортировка по имени курса | `/api/courses/?ordering=name` |
| `/api/lessons/` | `course` | id курса | Фильтр уроков по курсу | `/api/lessons/?course=1` |
| `/api/lessons/` | `search` | строка | Поиск урока по имени | `/api/lessons/?search=API` |
| `/api/lessons/` | `ordering` | `name` | Сортировка уроков по имени | `/api/lessons/?ordering=name` |
| `/api/payments/` | `course` | id курса | Фильтр платежей по курсу | `/api/payments/?course=1` |
| `/api/payments/` | `lesson` | id урока | Фильтр платежей по уроку | `/api/payments/?lesson=2` |
| `/api/payments/` | `payment_type` | `cash` / `card` | Фильтр по способу оплаты | `/api/payments/?payment_type=cash` |
| `/api/payments/` | `user` | id пользователя | Фильтр платежей по пользователю | `/api/payments/?user=1` |
| `/api/payments/` | `search` | строка | Поиск по имени или email пользователя | `/api/payments/?search=ivan` |
| `/api/payments/` | `ordering` | `payment_date` | Сортировка платежей по дате | `/api/payments/?ordering=-payment_date` |
