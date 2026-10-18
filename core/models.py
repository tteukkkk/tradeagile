from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class ProdutoAlertaEstoque(models.Model):
    id = models.AutoField(primary_key=True)
    produto_id = models.IntegerField()
    produto = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    quantidade_estoque = models.IntegerField()
    
    class Meta:
        managed = False
        
        db_table = 'vw_produto_alerta_estoque'

class ProdutosEsgotados(models.Model):
    id = models.IntegerField(primary_key=True)
    produto_nome = models.CharField(max_length=200)
    categoria_nome = models.CharField(max_length=100)
    
    class Meta:
        managed = False
        db_table = 'vw_produtos_esgotados'

class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.IntegerField(default=0)
    data_insercao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
    
    @property
    def valor_total_estoque(self):
        preco = self.preco or 0
        quantidade = self.quantidade_estoque or 0
        return preco * quantidade

class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('E', 'Entrada'),
        ('S', 'Saída'),
    ]
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    data = models.DateTimeField(auto_now_add=True)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome}"
    
    @property
    def valor_financeiro_movimentacao(self):
        quantidade = self.quantidade or 0
        preco = self.produto.preco or 0
        return quantidade *  preco
    
class Pedido(models.Model):
    FORMAS_PAGAMENTO = (
        ('PIX', 'Pix'),
        ('CREDITO', 'Cartão de Crédito'),
        ('DEBITO', 'Cartão de Débito'),
        ('BOLETO', 'Boleto Bancário'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(max_length=50, choices=FORMAS_PAGAMENTO, null=True, blank=True)

    
    def __str__(self):
        return f"Pedido #{self.id} - {self.status}"
    
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} Pedido #{self.pedido.id}"
    
    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

class Carrinho(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    produtos = models.ManyToManyField(Produto, through='ItemCarrinho')
    
    def __str__(self):
        return f"Carrinho de {self.usuario.username}"

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveBigIntegerField(default=1)
    adicionado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} no carrinho de {self.carrinho.usuario.username}"
    
    @property
    def subtotal(self):
        return self.quantidade * self.produto.preco