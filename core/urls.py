from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),  
    path('', views.dashboard, name='home'),
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('produto/novo/', views.produto_cadastrar, name='produto_cadastrar'),
    path('produto/editar/<int:id>/', views.produto_editar, name='produto_editar'),
    path('produto/excluir/<int:id>/', views.produto_excluir, name='produto_excluir'),
    path('categorias/', views.categoria_listar, name='categoria_listar'),
    path('categorias/importar/', views.importar_categorias, name='importar_categorias'),
    path('usuarios/', views.usuario_listar, name='usuario_listar'),
    path('categoria/nova/', views.categoria_cadastrar, name='categoria_cadastrar'),
    path('categoria/editar/<int:id>/', views.categoria_editar, name='categoria_editar'),
    path('categoria/excluir/<int:id>/', views.categoria_excluir, name='categoria_excluir'),
    path('alertas/', views.painel_alertas, name='painel_alertas'),
    path('reajuste/', views.reajuste_precos, name='reajuste_precos'),
    path('black-friday/', views.black_friday, name='black_friday'),
    path('produto/<int:produto_id>/movimentar/', views.registrar_movimentacao, name='registrar_movimentacao'),
    path('esgotados/', views.produtos_esgotados, name='produtos_esgotados'),
    path('loja/', views.loja, name='loja'),
    path('loja/carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('loja/carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('loja/carrinho/remover/<int:item_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('loja/finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('loja/meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
]