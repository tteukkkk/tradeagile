from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction
from decimal import Decimal, InvalidOperation
from .models import Produto, Categoria, ProdutoAlertaEstoque, ProdutosEsgotados, MovimentacaoEstoque
from .forms import ProdutoForm, CategoriaForm
from django.db.models import Q
from django.contrib import messages
import csv
import json
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, F
from .models import Categoria
from .models import Carrinho, ItemCarrinho, Pedido, ItemPedido

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

@login_required
def dashboard(request):
    produtos = Produto.objects.all()
    categorias = Categoria.objects.all()

    busca_nome = request.GET.get('q', '')
    busca_categoria = request.GET.get('categoria', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    ordenacao = request.GET.get('sort', '-data_insercao')

    if busca_nome:
        produtos = produtos.filter(nome__icontains=busca_nome)

    if busca_categoria:
        produtos = produtos.filter(categoria_id=busca_categoria)

    if data_inicio:
        data_inicio_completa = f"{data_inicio} 00:00:00"
        produtos = produtos.filter(data_insercao__gte=data_inicio_completa)

    if data_fim:
        data_fim_completa = f"{data_fim} 23:59:59"
        produtos = produtos.filter(data_insercao__lte=data_fim_completa)

    produtos = produtos.order_by(ordenacao)

    contexto = {
        'produtos': produtos,
        'categorias': categorias,
        'busca_nome': busca_nome,
        'busca_categoria': busca_categoria,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ordenacao': ordenacao,
    }
    return render(request, 'core/dashboard.html', contexto)

@login_required
def produto_cadastrar(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProdutoForm()
    return render(request, 'core/produto_form.html', {'form': form, 'acao': 'Cadastrar'})

@login_required
def produto_editar(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'core/produto_form.html', {'form': form, 'acao': 'Editar'})

@login_required
def produto_excluir(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        produto.delete()
        return redirect('dashboard')
    return render(request, 'core/produto_confirm_delete.html', {'produto': produto})

@login_required
def categoria_listar(request):
    busca = request.GET.get('q', '').strip()
    categorias = Categoria.objects.all()
    if busca:
        categorias = categorias.filter(
            Q(nome__icontains=busca) | Q(descricao__icontains=busca)
        )
    return render(request, 'core/categoria_listar.html', {
        'categorias': categorias,
        'busca': busca,
    })

@login_required
def usuario_listar(request):
    busca = request.GET.get('q', '').strip()
    usuarios = User.objects.all()
    if busca:
        usuarios = usuarios.filter(
            Q(username__icontains=busca) |
            Q(email__icontains=busca) |
            Q(first_name__icontains=busca) |
            Q(last_name__icontains=busca)
        )
    return render(request, 'core/usuario_listar.html', {
        'usuarios': usuarios,
        'busca': busca,
    })

@login_required
def importar_categorias(request):
    if request.method == 'POST' and request.FILES.get('arquivo'):
        arquivo = request.FILES['arquivo']
        extensao = arquivo.name.split('.')[-1].lower()

        if extensao != 'csv':
            messages.error(request, 'Formato inválido. Envie apenas .csv')
            return redirect('importar_categorias')

        try:
            decoded_file = arquivo.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            contador_sucesso = 0

            for linha in reader:
                nome = (linha.get('nome') or '').strip()
                descricao = (linha.get('descricao') or '').strip()
                if not nome:
                    continue

                Categoria.objects.update_or_create(
                    nome__iexact=nome,
                    defaults={'nome': nome, 'descricao': descricao}
                )
                contador_sucesso += 1

            messages.success(request, f'Importação concluída! {contador_sucesso} categorias cadastradas.')
            return redirect('categoria_listar')
        except Exception as e:
            messages.error(request, f'Erro ao processar arquivo: {str(e)}')
            return redirect('importar_categorias')

    return render(request, 'core/importar_categorias.html')

@login_required
def categoria_cadastrar(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categoria_listar')
    else:
        form = CategoriaForm()
    return render(request, 'core/categoria_form.html', {'form': form, 'acao': 'Cadastrar'})

@login_required
def categoria_editar(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('categoria_listar')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'core/categoria_form.html', {'form': form, 'acao': 'Editar'})

@login_required
def categoria_excluir(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        categoria.delete()
        return redirect('categoria_listar')
    return render(request, 'core/categoria_confirm_delete.html', {'categoria': categoria})

@login_required
def painel_alertas(request):
    alertas = [{'id': p.id, 'produto_id': p.id, 'produto': p.nome, 'categoria': p.categoria.nome, 'quantidade_estoque': p.quantidade_estoque} for p in Produto.objects.filter(quantidade_estoque__lte=10).select_related('categoria')]
    return render(request, 'core/alertas.html', {'alertas': alertas})

@login_required
def reajuste_precos(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria_id')
        percentual = request.POST.get('percentual')
    
        try:
            fator = Decimal('1') + Decimal(percentual) / Decimal('100')
            if not fator.is_finite() or fator < 0:
                raise ValueError
            categoria = get_object_or_404(Categoria, pk=categoria_id)
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, 'Percentual inválido.')
            return redirect('reajuste_precos')
        with transaction.atomic():
            for produto in Produto.objects.select_for_update().filter(categoria=categoria):
                produto.preco = (produto.preco * fator).quantize(Decimal('0.01'))
                produto.save(update_fields=['preco'])
        return redirect('dashboard')
    
    categorias = Categoria.objects.all()
    return render(request, 'core/reajuste_precos.html', {'categorias': categorias})

@login_required
def black_friday(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria_id')
        categoria = get_object_or_404(Categoria, pk=categoria_id)
        with transaction.atomic():
            for produto in Produto.objects.select_for_update().filter(categoria=categoria):
                produto.preco = (produto.preco * Decimal('0.90')).quantize(Decimal('0.01'))
                produto.save(update_fields=['preco'])
        return redirect('dashboard')

    categorias = Categoria.objects.all()
    return render(request, 'core/black_friday_form.html', {'categorias': categorias})

@login_required
def registrar_movimentacao(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        quantidade_informada = request.POST.get('quantidade')
        tipo_movimentacao = request.POST.get('tipo')
        
        
        try:
            quantidade = int(quantidade_informada)
            if quantidade <= 0 or tipo_movimentacao not in {'E', 'S'}:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Quantidade ou tipo inválido.')
            return redirect('registrar_movimentacao', produto_id=produto_id)
        with transaction.atomic():
            produto = Produto.objects.select_for_update().get(pk=produto.pk)
            if tipo_movimentacao == 'S' and quantidade > produto.quantidade_estoque:
                messages.error(request, 'Estoque insuficiente.')
                return redirect('registrar_movimentacao', produto_id=produto_id)
            produto.quantidade_estoque += quantidade if tipo_movimentacao == 'E' else -quantidade
            produto.save(update_fields=['quantidade_estoque'])
            MovimentacaoEstoque.objects.create(produto=produto, tipo=tipo_movimentacao, quantidade=quantidade, responsavel=request.user)
        return redirect('dashboard')
    return render(request, 'core/movimentacao_form.html', {'produto': produto})


@login_required
def produtos_esgotados(request):
    esgotados = Produto.objects.filter(quantidade_estoque=0).select_related('categoria')
    return render(request, 'core/esgotados.html', {'esgotados': esgotados})

@login_required
def importar_produtos(request):
    if request.method == 'POST' and request.FILES.get('arquivo'):
        arquivo = request.FILES['arquivo'] 
        extensao = arquivo.name.split('.')[-1].lower()

        contador_sucesso = 0

        try:
            if extensao == 'csv':
                decoded_file = arquivo.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                for linha in reader:
                    Produto.objects.create(
                        categoria_id=linha.get('categoria_id'),
                        nome=linha.get('nome'),
                        preco=linha.get('preco'),
                        quantidade_estoque=linha.get('quantidade_estoque', 0)
                    )
                    contador_sucesso += 1

            elif extensao == 'json':
                dados = json.load(arquivo)  
                for item in dados:
                    Produto.objects.create(
                        categoria_id=item.get('categoria_id'),
                        nome=item.get('nome'),
                        preco=item.get('preco'),
                        quantidade_estoque=item.get('quantidade_estoque', 0)
                    )
                    contador_sucesso += 1

            else:
                messages.error(request, 'Formato inválido. Envie apenas .csv ou .json')
                return redirect('importar_produtos')

            messages.success(request, f'Importação concluída! {contador_sucesso} produtos cadastrados.')
            return redirect('dashboard')  

        except Exception as e:
            messages.error(request, f'Erro ao processar arquivo: {str(e)}') 
            return redirect('importar_produtos')

    return render(request, 'core/importar.html')

@login_required
def relatorio_valor_estoque(request):
    produtos = Produto.objects.all().order_by('nome')
    movimentacoes = MovimentacaoEstoque.objects.all().order_by('-data')[:10]
    total_geral_empresa = sum(p.valor_total_estoque for p in produtos)
    contexto = {
        'produtos': produtos,
        'movimentacoes': movimentacoes,
        'total_geral': total_geral_empresa,
    }
    return render(request, 'core/relatorio_estoque.html', contexto)

@login_required
def grafico_estoque_categoria(request):
    busca_categoria = request.GET.get('q', '').strip()
    categorias = Categoria.objects.annotate(
        total_investido=Sum(F('produto__quantidade_estoque') * F('produto__preco'))
    )

    if busca_categoria:
        categorias = categorias.filter(nome__icontains=busca_categoria)

    categorias = categorias.order_by('-total_investido')
    labels = [cat.nome for cat in categorias]
    data = [float(cat.total_investido or 0) for cat in categorias]
    contexto = {
        'labels': labels,
        'data': data,
        'busca_categoria': busca_categoria,
    }
    return render(request, 'core/grafico_estoque.html', contexto)

def loja(request):
    produtos = Produto.objects.filter(quantidade_estoque__gt=0)
    return render(request, 'core/loja.html', {'produtos': produtos})

@login_required
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)
    item, created = ItemCarrinho.objects.get_or_create(carrinho=carrinho, produto=produto)

    if not created:
        item.quantidade += 1
        item.save()

    messages.success(request, f'Produto "{produto.nome}" foi adicionado ao seu carrinho.')
    
    return redirect('loja')

@login_required
def ver_carrinho(request):
    carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
    itens = ItemCarrinho.objects.filter(carrinho=carrinho)
    total = sum(item.produto.preco * item.quantidade for item in itens)
    
    return render(request, 'core/carrinho.html', {'itens': itens, 'total': total})

@login_required
def remover_do_carrinho(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user)
    item.delete()
    messages.success(request, 'Produto removido do carrinho.')
    
    return redirect('ver_carrinho')

@login_required
def finalizar_compra(request):
    carrinho = get_object_or_404(Carrinho, usuario=request.user)
    itens = list(ItemCarrinho.objects.filter(carrinho=carrinho).select_related('produto'))
    if not itens:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('loja')
    total = sum((item.subtotal for item in itens), Decimal('0'))
    if request.method == 'POST':
        forma = request.POST.get('forma_pagamento')
        valor = request.POST.get('valor_pago', '0').strip()
        if ',' in valor:
            valor = valor.replace('.', '').replace(',', '.')
        try:
            pago = Decimal(valor)
            if not pago.is_finite() or pago.quantize(Decimal('0.01')) != total or forma not in dict(Pedido.FORMAS_PAGAMENTO):
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, 'Confira o valor e a forma de pagamento.')
            return render(request, 'core/checkout.html', {'itens': itens, 'total': total})
        with transaction.atomic():
            produtos = {p.id: p for p in Produto.objects.select_for_update().filter(id__in=[i.produto_id for i in itens]).order_by('id')}
            if any(i.quantidade <= 0 or produtos[i.produto_id].quantidade_estoque < i.quantidade for i in itens):
                messages.error(request, 'Estoque insuficiente.')
                return redirect('ver_carrinho')
            # O pagamento é somente uma simulação acadêmica.
            pedido = Pedido.objects.create(usuario=request.user, status='Aprovado', valor_total=total, forma_pagamento=forma)
            for item in itens:
                produto = produtos[item.produto_id]
                ItemPedido.objects.create(pedido=pedido, produto=produto, quantidade=item.quantidade, preco_unitario=produto.preco)
                produto.quantidade_estoque -= item.quantidade
                produto.save(update_fields=['quantidade_estoque'])
                MovimentacaoEstoque.objects.create(produto=produto, tipo='S', quantidade=item.quantidade, responsavel=request.user)
            ItemCarrinho.objects.filter(carrinho=carrinho).delete()
        messages.success(request, f'Pedido #{pedido.id} registrado (pagamento simulado).')
        return redirect('meus_pedidos')
    return render(request, 'core/checkout.html', {'itens': itens, 'total': total})

@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
    return render(request, 'core/meus_pedidos.html', {'pedidos': pedidos})
