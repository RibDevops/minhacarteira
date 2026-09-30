from django.db import migrations, models


def dedupe_tipos(apps, schema_editor):
    """
    Corrige duplicatas de Tipo (ex: várias linhas 'D' = Saída) que puderam
    ser criadas porque o campo codigo não tinha unique=True. Mantém a linha
    de menor id por código, reatribui Cartao/Transacao/Recorrencia que
    apontavam pras duplicadas, e só então apaga as duplicadas.
    """
    Tipo = apps.get_model('cal', 'Tipo')
    Cartao = apps.get_model('cal', 'Cartao')
    Transacao = apps.get_model('cal', 'Transacao')
    Recorrencia = apps.get_model('cal', 'Recorrencia')

    canonico_por_codigo = {}
    for tipo in Tipo.objects.order_by('id'):
        canonico = canonico_por_codigo.get(tipo.codigo)
        if canonico is None:
            canonico_por_codigo[tipo.codigo] = tipo
            continue

        Cartao.objects.filter(tipo=tipo).update(tipo=canonico)
        Transacao.objects.filter(tipo=tipo).update(tipo=canonico)
        Recorrencia.objects.filter(tipo=tipo).update(tipo=canonico)
        tipo.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0005_consolidate_formapagamento_cartao'),
    ]

    operations = [
        migrations.RunPython(dedupe_tipos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='tipo',
            name='codigo',
            field=models.CharField(
                max_length=1,
                choices=[('C', 'Crédito (Entrada)'), ('D', 'Débito (Saída)')],
                default='D',
                unique=True,
            ),
        ),
    ]
