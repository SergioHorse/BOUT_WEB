import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retoque', '0005_campolistado_grupos'),
        ('zaq', '0003_category_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retoque',
            name='allocation_retouching_cost',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='retoque.imputacionretoque', verbose_name='Imputación del retoque'),
        ),
        migrations.AlterField(
            model_name='retoque',
            name='engine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='retoques', to='zaq.engine', verbose_name='Motor'),
        ),
        migrations.AlterField(
            model_name='retoque',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='retoque.estadoretoque', verbose_name='Estado actual'),
        ),
    ]
