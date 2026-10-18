# TradeAgile

Sistema de gestão de estoque e loja acadêmica com autenticação, filtros, importação CSV/JSON, relatórios e pedidos.

**Autor:** Matheus Macêdo Felicio · Técnico em Desenvolvimento de Sistemas — SENAI  
**Tecnologias:** Python, Django, HTML/CSS e SQLite; configuração opcional para MySQL.

## Funcionalidades

- Cadastro de produtos e categorias
- Busca, filtros por data e ordenação
- Importação CSV e JSON
- Alertas de estoque, reajuste e promoção por categoria
- Relatório financeiro e gráfico por categoria
- Carrinho e histórico de pedidos com pagamento simulado

## Executar localmente

Requisitos: Python 3.12 e Git. Os testes desta versão foram executados com Python 3.12.14 e Django 5.2.18.

```bash
git clone https://github.com/tteukkkk/tradeagile.git
cd tradeagile
python -m venv .venv
```

Ative o ambiente:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instale as dependências, prepare o banco e inicie:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abra <http://127.0.0.1:8000/>. O banco SQLite é criado localmente; não há usuários ou senhas predefinidos no repositório.

Para sessões estáveis entre reinícios, copie `.env.example` para `.env` e defina `DJANGO_SECRET_KEY` com uma chave gerada por:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

O `.env` é carregado automaticamente e não deve ser versionado. Sem chave configurada, o projeto gera uma chave temporária a cada inicialização, invalidando as sessões no reinício.

## Dados de demonstração

Criar categorias e produtos pelo painel ou pelo admin. A importação de categorias usa colunas `nome,descricao`; a de produtos usa `categoria_id,nome,preco,quantidade_estoque`. Valores decimais usam ponto nos arquivos.

## Testes

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

**Resultado desta revisão:** 4 testes passaram em SQLite. `check` não apontou problemas e não há migrações pendentes. Veja [os detalhes da revisão](docs/REVISAO.md).

## Rotas principais

| Caminho local |
| --- |
| `/accounts/login/` |
| `/dashboard/` |
| `/loja/` |
| `/alertas/` |
| `/admin/` |

## Organização

- `tradeagile_project/`: configuração, rotas principais e entrada ASGI/WSGI.
- Apps `core`: regras, modelos, formulários e rotas de cada módulo.
- `templates/` ou pastas de templates nos apps: interface original.
- `static/` ou pastas static dos apps: estilos e recursos originais.
- `requirements.txt`: dependências da demonstração.
- `.env.example`: modelo de configuração local.
- `docs/REVISAO.md`: alterações e alcance da validação.

## MySQL opcional

O projeto original pode ser executado com MySQL, mas esta revisão foi testada **somente em SQLite**. Instale o servidor MySQL e os requisitos de compilação do mysqlclient para seu sistema, crie um banco vazio e um usuário local com permissões sobre esse banco e execute:

```bash
python -m pip install -r requirements-mysql.txt
```

No `.env`, configure `DB_ENGINE=mysql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT`; depois execute as migrações. MySQL e concorrência entre requisições não foram testados neste ambiente.

## Limitações conhecidas

As rotinas SQL não acompanhavam o ZIP. Alertas, reajustes e baixa de estoque foram adaptados para o ORM, com transações e validação de quantidade. Pagamento é uma simulação local; não existe gateway bancário. Os modelos legados de views MySQL permanecem como referência, mas não são usados pelo painel.

O projeto é uma demonstração de aprendizado. A configuração padrão usa DEBUG para desenvolvimento; publicação do código no GitHub não equivale à implantação de um serviço web.

## Origem

Baseado no projeto acadêmico enviado pelo autor. Organização, configuração e correções desta revisão estão descritas em `docs/REVISAO.md`. O visual original foi preservado; nomes, marcas e recursos temáticos pertencem aos respectivos titulares.
