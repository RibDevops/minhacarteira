from datetime import date
from django.db.models import Sum
from .models import Transacao

def saldos_mensais(request):
    print(">>> Context Processor CHAMADO <<<")
    if not request.user.is_authenticated:
        return {}

    user = request.user
    hoje = date.today()

    # Saldo mês atual
    transacoes_mes = Transacao.objects.filter(
        user=user,
        data__year=hoje.year,
        data__month=hoje.month
    )
    print(f'transacoes_mes: {transacoes_mes}')
    total_creditos = transacoes_mes.filter(tipo__is_credito=True).aggregate(total=Sum('valor'))['total'] or 0
    total_debitos = transacoes_mes.filter(tipo__is_credito=False).aggregate(total=Sum('valor'))['total'] or 0
    saldo_total = total_creditos - total_debitos
    print(f'saldo_total: {saldo_total}')

    # Próximo mês
    if hoje.month == 12:
        proximo_ano = hoje.year + 1
        proximo_mes = 1
    else:
        proximo_ano = hoje.year
        proximo_mes = hoje.month + 1

    transacoes_prox_mes = Transacao.objects.filter(
        user=user,
        data__year=proximo_ano,
        data__month=proximo_mes
    )
    total_creditos_prox = transacoes_prox_mes.filter(tipo__is_credito=True).aggregate(total=Sum('valor'))['total'] or 0
    total_debitos_prox = transacoes_prox_mes.filter(tipo__is_credito=False).aggregate(total=Sum('valor'))['total'] or 0
    saldo_total_prox = total_creditos_prox - total_debitos_prox

    return {
        'saldo_total_nav': saldo_total,
        'saldo_total_prox_nav': saldo_total_prox,
        'month_name': hoje.strftime("%B"),
        'mes_proximo_nome': date(proximo_ano, proximo_mes, 1).strftime("%B"),
        'total_creditos': total_creditos,
        'total_debitos': total_debitos,
        'total_creditos_prox': total_creditos_prox,
        'total_debitos_prox': total_debitos_prox,
    }
