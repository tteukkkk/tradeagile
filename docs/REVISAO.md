# Revisão para portfólio

## Alterações comuns

- Removidos ambientes virtuais, arquivos compilados, bancos SQLite, uploads locais e estáticos coletados.
- Configuração de credenciais por variáveis de ambiente; arquivo `.env.example` sem senha real.
- SQLite como padrão para demonstração e MySQL opcional.
- Dependências e instruções de instalação documentadas.
- DEFAULT_AUTO_FIELD alinhado às migrações existentes.

## Alterações específicas

Controle de estoque atualizado junto ao histórico; checkout com validação de saldo de estoque e valores monetários com Decimal. Alertas e reajustes sem dependência de views/procedures externas; removida rota admin duplicada.

## Verificação executada

Python 3.12.14 / Django 5.2.18 / SQLite. 4 testes passaram; check, conferência de migrações e migrate concluíram com sucesso. Testes novos cobrem fluxos alterados e se somam aos testes originais. Não houve teste de MySQL, concorrência real, implantação ou inspeção visual em navegador da aplicação local.

## Limitações

As rotinas SQL não acompanhavam o ZIP. Alertas, reajustes e baixa de estoque foram adaptados para o ORM, com transações e validação de quantidade. Pagamento é uma simulação local; não existe gateway bancário. Os modelos legados de views MySQL permanecem como referência, mas não são usados pelo painel.

## Modelos principais

- `Categoria`
- `Produto`
- `MovimentacaoEstoque`
- `Carrinho`
- `ItemCarrinho`
- `Pedido`
- `ItemPedido`
