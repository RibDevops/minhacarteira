from django.db import migrations, models
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('cal', '0006_dedupe_tipo_unique'),
    ]
    operations = [
        migrations.AddField(
            model_name='transacao',
            name='uuid',
            field=models.UUIDField(null=True, unique=True, editable=False),
        ),
        migrations.AddField(
            model_name='transacao',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='recorrencia',
            name='uuid',
            field=models.UUIDField(null=True, unique=True, editable=False),
        ),
        migrations.AddField(
            model_name='recorrencia',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
    ]
