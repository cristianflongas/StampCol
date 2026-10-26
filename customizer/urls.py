from django.urls import path
from . import views

app_name = 'customizer'

urlpatterns = [
    # Vista principal interactiva
    path('', views.index, name='index'),
    
    # Endpoint de Monitoreo / Keep-Alive para UptimeRobot (24/7 activo en Render)
    path('health/', views.health_check, name='health_check'),
    path('ping/', views.health_check, name='ping'),
    
    # Endpoint del Asistente IA Gemini
    path('api/gemini-assistant/', views.gemini_assistant_view, name='gemini_assistant'),
    
    # Endpoint para guardar pedido y generar enlace de WhatsApp
    path('api/save-order/', views.save_order, name='save_order'),

    # Endpoints de IA para estampados (quitar fondo / aislar captura y visión)
    path('api/isolate-stamp/', views.isolate_stamp, name='isolate_stamp'),
    path('api/analyze-stamp-vision/', views.analyze_stamp_vision, name='analyze_stamp_vision'),
    path('api/fetch-external-image/', views.fetch_external_image, name='fetch_external_image'),

    # Ficha técnica oficial y previsualización de pedidos
    path('order/<int:order_id>/', views.order_preview, name='order_preview'),

    # Endpoint de limpieza / purga de mockups tras visualización
    path('api/orders/<int:order_id>/purge-mockup/', views.purge_order_mockup, name='purge_order_mockup'),
]

