from django.shortcuts import render
from ..models import Transacao
from cal import models

def dashboard(request):
    user = request.user
    # Filtrar transações do usuário
    transacoes = Transacao.objects.filter(fk_user=user)

    # Somar os valores por categoria
    credito = transacoes.filter(categoria='CREDITO').aggregate(total=models.Sum('valor'))['total'] or 0
    debito = transacoes.filter(categoria='DEBITO').aggregate(total=models.Sum('valor'))['total'] or 0
    salario = transacoes.filter(categoria='SALARIO').aggregate(total=models.Sum('valor'))['total'] or 0
    emprestimo = transacoes.filter(categoria='EMPRESTIMO').aggregate(total=models.Sum('valor'))['total'] or 0
    cripto = transacoes.filter(categoria='CRIPTO').aggregate(total=models.Sum('valor'))['total'] or 0

    # Calcular o saldo
    saldo = credito - debito

    # Verificar se está em crédito ou débito
    estado = "Crédito" if saldo >= 0 else "Débito"

    # Renderizar na página
    return render(request, 'dashboard.html', {
        'credito': credito,
        'debito': debito,
        'saldo': saldo,
        'estado': estado,
        'salario': salario,
        'emprestimo': emprestimo,
        'cripto': cripto,
    })

from datetime import timedelta

def processar_transacoes_recorrentes():
    transacoes_recorrentes = Transacao.objects.filter(fk_user=user, recorrente=True)
    for transacao in transacoes_recorrentes:
        if transacao.data < datetime.now().date():
            # Criar uma nova transação para o próximo período (por exemplo, mensal)
            nova_transacao = Transacao(
                fk_user=transacao.fk_user,
                titulo=transacao.titulo,
                valor=transacao.valor,
                data=transacao.data + timedelta(days=30),  # Ajuste conforme o período
                categoria=transacao.categoria,
                recorrente=True
            )
            nova_transacao.save()
