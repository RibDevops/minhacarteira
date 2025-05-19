# cal/context_processors.py

from .models import Transacao
from django.db.models import Sum
from datetime import date

def saldo_context(request):
    if not request.user.is_authenticated:
        return {}

    hoje = date.today()

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__year=hoje.year,
        data__month=hoje.month
    )

    total_creditos = transacoes.filter(tipo__is_credito=True).aggregate(total=Sum('valor'))['total'] or 0
    total_debitos = transacoes.filter(tipo__is_credito=False).aggregate(total=Sum('valor'))['total'] or 0
    saldo_total = total_creditos - total_debitos

    return {
        'saldo_total_global': saldo_total,
    }
