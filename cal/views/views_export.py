import csv
from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from ..models import Tipo, Transacao
from ..utils import parse_mes_ano, intervalo_do_mes


@login_required
def exportar_transacoes_csv(request):
    ano, mes = parse_mes_ano(request)
    data_inicio, data_fim = intervalo_do_mes(ano, mes)

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria', 'cartao').order_by('data')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="transacoes_{mes}_{ano}.csv"'
    response.write(u'\ufeff'.encode('utf8'))  # BOM para Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Data', 'Título', 'Categoria', 'Tipo', 'Cartão', 'Valor'])

    for t in transacoes:
        # Proteção contra CSV Injection: prefixa com ' se começar com =, +, -, @
        titulo = t.titulo or ''
        if titulo and titulo[0] in ('=', '+', '-', '@'):
            titulo = "'" + titulo

        writer.writerow([
            t.data.strftime('%d/%m/%Y'),
            titulo,
            t.categoria.nome if t.categoria else '-',
            t.tipo.descricao,
            t.cartao.nome if t.cartao else '-',
            str(t.valor).replace('.', ',')
        ])

    return response
