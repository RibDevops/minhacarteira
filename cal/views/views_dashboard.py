from decimal import Decimal
from django.shortcuts import render
from ..models import Transacao
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from datetime import date
from collections import OrderedDict, defaultdict

@login_required
def dashboard(request):
    user = request.user
    hoje = date.today()
    ano_selecionado = int(request.GET.get('ano', hoje.year))
    
    # Todos os meses do ano selecionado
    transacoes_ano = Transacao.objects.filter(
        user=user, 
        data__year=ano_selecionado
    ).select_related('tipo', 'categoria')

    # Resumo Anual
    credito_anual = Decimal('0')
    debito_anual = Decimal('0')
    for t in transacoes_ano:
        val = t.valor_decimal
        if t.tipo.codigo == 'C':
            credito_anual += val
        else:
            debito_anual += val
    saldo_anual = credito_anual - debito_anual

    # Detalhamento por Mês
    meses_detalhe = OrderedDict()
    nomes_meses = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    for mes_num in range(1, 13):
        transacoes_mes = [t for t in transacoes_ano if t.data.month == mes_num]
        
        c_mes = sum((t.valor_decimal for t in transacoes_mes if t.tipo.codigo == 'C'), Decimal('0'))
        d_mes = sum((t.valor_decimal for t in transacoes_mes if t.tipo.codigo == 'D'), Decimal('0'))
        s_mes = c_mes - d_mes
        
        # Dados para o gráfico do mês (por categoria)
        cat_sums = defaultdict(Decimal)
        for t in transacoes_mes:
            cat_name = t.categoria.nome if t.categoria else 'Sem Categoria'
            cat_sums[cat_name] += t.valor_decimal
            
        meses_detalhe[mes_num] = {
            'nome': nomes_meses[mes_num],
            'credito': c_mes,
            'debito': d_mes,
            'saldo': s_mes,
            'grafico_labels': list(cat_sums.keys()),
            'grafico_valores': [float(v) for v in cat_sums.values()],
            'tem_dados': len(transacoes_mes) > 0
        }

    anos_disponiveis = range(hoje.year - 5, hoje.year + 2)

    return render(request, 'cal/dashboard.html', {
        'ano_selecionado': ano_selecionado,
        'anos_disponiveis': anos_disponiveis,
        'credito_anual': credito_anual,
        'debito_anual': debito_anual,
        'saldo_anual': saldo_anual,
        'meses_detalhe': meses_detalhe,
    })
