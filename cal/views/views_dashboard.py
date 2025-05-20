from django.shortcuts import render
from ..models import Transacao
from cal import models
from django.db.models import Sum

def dashboard(request):
    user = request.user
    transacoes = Transacao.objects.filter(user=user)

    credito = transacoes.filter(tipo__is_credito=True).aggregate(total=Sum('valor'))['total'] or 0
    debito = transacoes.filter(tipo__is_credito=False).aggregate(total=Sum('valor'))['total'] or 0

    saldo = credito - debito
    estado = "Crédito" if saldo >= 0 else "Débito"

    return render(request, 'dashboard.html', {
        'saldo_total': saldo,
        'total_creditos': credito,
        'total_debitos': debito,
        'estado': estado,
        'transacoes': transacoes,
    })
