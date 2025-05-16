from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from cal.models import Transacao

def transacoes_mes_context(request):
    if not request.user.is_authenticated:
        return {}

    hoje = timezone.localtime(timezone.now())  # timezone-aware data/hora atual no fuso configurado
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fim_mes = inicio_mes + relativedelta(months=1)

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=inicio_mes,
        data__lt=fim_mes
    )

    total_creditos = transacoes.filter(tipo__descricao__iexact='CRÉDITO').aggregate(total=Sum('valor'))['total'] or 0
    total_debitos = transacoes.filter(tipo__descricao__iexact='DÉBITO').aggregate(total=Sum('valor'))['total'] or 0
    saldo_total = total_creditos - total_debitos

    return {
        'total_creditos': total_creditos,
        'total_debitos': total_debitos,
        'saldo_total': saldo_total,
    }




# from datetime import date, datetime
# from dateutil.relativedelta import relativedelta
# from collections import defaultdict
# from decimal import Decimal
# from django.utils.timezone import make_aware
# from cal.models import Transacao
# from django.db.models import Sum

# def transacoes_mes_context(request):
#     if not request.user.is_authenticated:
#         return {}

#     ano = int(request.GET.get('ano', date.today().year))
#     mes = int(request.GET.get('mes', date.today().month))

#     data_inicio = make_aware(datetime(ano, mes, 1))
#     data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

#     transacoes = Transacao.objects.filter(
#         user=request.user,
#         data__gte=data_inicio,
#         data__lt=data_fim
#     )

#     total_creditos = transacoes.filter(tipo__descricao__iexact='CRÉDITO').aggregate(total=Sum('valor'))['total'] or 0
#     total_debitos = transacoes.filter(tipo__descricao__iexact='DÉBITO').aggregate(total=Sum('valor'))['total'] or 0
#     saldo_total = total_creditos - total_debitos

#     return {
#         'total_creditos': total_creditos,
#         'total_debitos': total_debitos,
#         'saldo_total': saldo_total,
#     }
