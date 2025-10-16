from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # JSON-схема (генерация OpenAPI)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI (интерактивная документация)
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc (альтернатива Swagger)
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]