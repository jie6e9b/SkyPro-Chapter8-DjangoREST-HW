API 

Запросы в postman 

POST - http://127.0.0.1:8000/api/courses/

{
    "name": "Django REST Framework",
    "preview": null,
    "description": "Изучаем DRF"
}

{
    "name": "Python",
    "preview": null,
    "description": "Изучаем Python"
}

{
    "name": "Postgres",
    "preview": null,
    "description": "Изучаем Postgres"
}


Проверка в Postman
	•	Курсы (ViewSet, router):
	•	GET /api/courses/
	•	POST /api/courses/
	•	GET /api/courses/1/
	•	PUT /api/courses/1/
	•	DELETE /api/courses/1/

Уроки (GenericAPIView):
	•	GET /api/lessons/
	•	POST /api/lessons/
	•	GET /api/lessons/1/
	•	PUT/PATCH /api/lessons/1/
	•	DELETE /api/lessons/1/

Пользователь (доп.)
	•	GET /api/users/1/
	•	PUT /api/users/1/