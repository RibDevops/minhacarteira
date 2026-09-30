from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('cal', '0008_populate_uuid'),
    ]
    operations = [
        migrations.AlterField(
            model_name='transacao',
            name='uuid',
            field=models.UUIDField(null=False, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='transacao',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='recorrencia',
            name='uuid',
            field=models.UUIDField(null=False, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='recorrencia',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
