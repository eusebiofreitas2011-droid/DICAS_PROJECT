from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    path('',                          views.redirecionar_inicio, name='inicio'),
    path('upload/',                   views.upload_documento,    name='upload'),
    path('documentos/',               views.lista_documentos,    name='lista'),
    path('documentos/<int:pk>/',      views.detalhe_documento,   name='detalhe'),
    path('documentos/<int:pk>/validar/', views.validar_documento, name='validar'),
    path('documentos/<int:pk>/estado/',  views.estado_documento,  name='estado'),
]
