from django.shortcuts import render
from ..models import Transacao
from cal import models

def dashboard(request):
    user = request.user
    # Filtrar transações do usuário
    transacoes = Transacao.objects.filter(user=user)


    # Somar os valores por tipo
    # credito = transacoes.filter(is_credito=True).aggregate(total=models.Sum('valor'))['total'] or 0
    # debito = transacoes.filter(is_credito=False).aggregate(total=models.Sum('valor'))['total'] or 0

    credito = transacoes.filter(tipo__is_credito=True).aggregate(total=models.Sum('valor'))['total'] or 0
    print(">>> credito:", credito)
    debito = transacoes.filter(tipo__is_credito=False).aggregate(total=models.Sum('valor'))['total'] or 0
    print(">>> debito:", debito)
    # salario = transacoes.filter(tipo='SALARIO').aggregate(total=models.Sum('valor'))['total'] or 0
    # emprestimo = transacoes.filter(tipo='EMPRESTIMO').aggregate(total=models.Sum('valor'))['total'] or 0
    # cripto = transacoes.filter(tipo='CRIPTO').aggregate(total=models.Sum('valor'))['total'] or 0

    # Calcular o saldo
    saldo = credito - debito

    # Verificar se está em crédito ou débito
    estado = "Crédito" if saldo >= 0 else "Débito"
    print(">>> Transações do usuário:", transacoes.count())
    for t in transacoes:
        print(f" - ID: {t.id} | valor: {t.valor} | tipo: {t.tipo}")
    print(">>> crédito:", credito)
    print(">>> débito:", debito)
    print(">>> saldo:", saldo)

    import pdb; pdb.set_trace()

    # Renderizar na página
    return render(request, 'dashboard.html', {
    'saldo_total': saldo,
    'total_creditos': credito,
    'total_debitos': debito,
    'estado': estado,
    'salario': salario,
    'emprestimo': emprestimo,
    'cripto': cripto,
    'transacoes': transacoes,  # <-- IMPORTANTE para renderizar a lista!
    })



from datetime import datetime, timedelta

