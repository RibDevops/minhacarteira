from datetime import date
from decimal import Decimal

from .models import Categoria, Cartao, Tipo, Transacao
from .services import saldos_consecutivos


def saldos_mensais(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user
    hoje = date.today()

    saldos = saldos_consecutivos(user, hoje.year, hoje.month)
    atual = saldos['atual']
    proximo = saldos['proximo']
    data_prox = saldos['proximo_data']

    return {
        'saldo_total_nav': atual['saldo'],
        'saldo_total_prox_nav': proximo['saldo'],
        'month_name': hoje.strftime("%B"),
        'mes_proximo_nome': data_prox.strftime("%B"),
        'total_creditos': atual['creditos'],
        'total_debitos': atual['debitos'],
        'total_creditos_prox': proximo['creditos'],
        'total_debitos_prox': proximo['debitos'],
        # Usados pelo modal global de "Registro Rápido" (menos cliques no FAB)
        'categorias_quick_add': Categoria.get_for_user(user),
        'tipos_quick_add': Tipo.objects.all(),
        'cartoes_quick_add': Cartao.objects.filter(user=user, is_active=True),
    }
