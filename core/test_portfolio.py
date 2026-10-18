from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Categoria, Produto, Carrinho, ItemCarrinho, Pedido, MovimentacaoEstoque

class EstoqueCheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', password='teste-local-123')
        self.client.force_login(self.user)
        cat = Categoria.objects.create(nome='Teste')
        self.produto = Produto.objects.create(categoria=cat, nome='Item', preco=Decimal('10.50'), quantidade_estoque=3)
        carrinho = Carrinho.objects.create(usuario=self.user)
        self.item = ItemCarrinho.objects.create(carrinho=carrinho, produto=self.produto, quantidade=2)

    def test_checkout_registra_itens_e_baixa_estoque(self):
        self.client.post(reverse('finalizar_compra'), {'forma_pagamento':'PIX', 'valor_pago':'21,00'})
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade_estoque, 1)
        self.assertEqual(Pedido.objects.get().valor_total, Decimal('21.00'))
        self.assertEqual(MovimentacaoEstoque.objects.count(), 1)
        self.assertFalse(ItemCarrinho.objects.exists())

    def test_saida_insuficiente_nao_altera_estoque(self):
        self.client.post(reverse('registrar_movimentacao', args=[self.produto.pk]), {'tipo':'S','quantidade':4})
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade_estoque, 3)
        self.assertFalse(MovimentacaoEstoque.objects.exists())

    def test_alertas_e_reajuste_sem_routines_externas(self):
        self.assertEqual(self.client.get(reverse('painel_alertas')).status_code, 200)
        self.client.post(reverse('reajuste_precos'), {'categoria_id': self.produto.categoria_id, 'percentual':'10'})
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.preco, Decimal('11.55'))

    def test_paginas_autenticadas(self):
        for name in ['dashboard','categoria_listar','usuario_listar','produtos_esgotados','relatorio_valor_estoque','grafico_estoque_categoria','loja','ver_carrinho','meus_pedidos']:
            with self.subTest(name=name): self.assertEqual(self.client.get(reverse(name)).status_code, 200)
