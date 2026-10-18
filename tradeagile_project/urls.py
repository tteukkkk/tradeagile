from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('produtos/importar/', views.importar_produtos, name='importar_produtos'),
    path('relatorio/valor-estoque/', views.relatorio_valor_estoque, name='relatorio_valor_estoque'),
    path('grafico/estoque-categoria/', views.grafico_estoque_categoria, name='grafico_estoque_categoria'),
]