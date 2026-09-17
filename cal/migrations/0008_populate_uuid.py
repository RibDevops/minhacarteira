from django.db import migrations
import uuid

def set_unique_uuid(apps, schema_editor):
    Transacao = apps.get_model('cal', 'Transacao')
    Recorrencia = apps.get_model('cal', 'Recorrencia')

    for obj in Transacao.objects.filter(uuid__isnull=True):
        obj.uuid = uuid.uuid4()
        obj.save(update_fields=['uuid'])

    for obj in Recorrencia.objects.filter(uuid__isnull=True):
        obj.uuid = uuid.uuid4()
        obj.save(update_fields=['uuid'])

class Migration(migrations.Migration):
    dependencies = [
        ('cal', '0007_add_uuid_nullable'),
    ]
    operations = [
        migrations.RunPython(set_unique_uuid, migrations.RunPython.noop),
    ]
