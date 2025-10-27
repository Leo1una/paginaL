from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("menu/", views.portada, name="portada"),
    path("plantillas/descargar/", views.plantillas, name="plantillas"),
    path("preescolar/", views.preescolar, name="preescolar"),
    path("preescolar/observaciones/", views.preescolarO, name="primaria_observaciones"),
    path("primaria/", views.primaria, name="primaria"),
    path("primaria/observaciones/", views.primaria_observaciones, name="primaria_observaciones"),
    path("primaria/planeacion/", views.primaria_planeacion, name="primaria_planeacion"),
    path("primaria/evaluaciones/", views.primaria_evaluaciones, name="primaria_evaluaciones"),
    path("secundaria/", views.secundaria, name="secundaria"),
    path("preparatoria/", views.preparatoria, name="preparatoria"),
    path('enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path("qrgenerador/", views.qr, name="qr"),
    path('generar_qr/', views.generar_qr, name='generar_qr'),
    path('maestros/', views.maestros, name='maestros'),
    path('calculadora/', views.calculadora, name='calculadora'),
    path("ruleta/", views.ruleta, name="ruleta"),
    path("generador/", views.generador, name="generador"),
    path("conversor/", views.conversor, name="conversor"),
]
