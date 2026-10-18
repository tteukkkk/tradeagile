# Generated migration to add produto_id field and recreate view

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_produtoalertaestoque'),
    ]

    operations = [
        # Drop the existing view
        migrations.RunSQL(
            "DROP VIEW IF EXISTS vw_produto_alerta_estoque;",
            "-- Recreate view if needed"
        ),
        # Add the produto_id field to the model (for Django ORM awareness)
        migrations.AddField(
            model_name='produtoalertaestoque',
            name='produto_id',
            field=models.IntegerField(null=True),
        ),
        # Recreate the view with produto_id column
        migrations.RunSQL(
            """
            CREATE VIEW vw_produto_alerta_estoque AS
            SELECT 
                p.id as id,
                p.id as produto_id,
                p.nome as produto,
                c.nome as categoria,
                p.quantidade_estoque as quantidade_estoque
            FROM core_produto p
            INNER JOIN core_categoria c ON p.categoria_id = c.id
            WHERE p.quantidade_estoque <= 10
            ORDER BY p.quantidade_estoque ASC;
            """,
            "DROP VIEW IF EXISTS vw_produto_alerta_estoque;"
        ),
    ]
