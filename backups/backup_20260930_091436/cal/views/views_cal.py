import calendar
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator
from django.views import generic

from cal.models import Transacao
from cal.services import saldos_consecutivos
from cal.utils import Calendar


def get_date(req_month):
    if req_month:
        try:
            if '.' in req_month:
                parts = req_month.split('-')
                if len(parts) >= 2:
                    year_str = parts[0].replace('.', '')
                    month_str = parts[1].replace('.', '')
                    year = int(year_str)
                    month = int(month_str)
                    return date(year, month, 1)

            if '-' in req_month:
                parts = req_month.split('-')
                if len(parts) >= 2:
                    year = int(parts[0])
                    month = int(parts[1])
                    return date(year, month, 1)

            year = int(req_month)
            return date(year, 1, 1)
        except (ValueError, TypeError):
            pass
    return date.today()


def prev_month(d):
    first = d.replace(day=1)
    prev = first - timedelta(days=1)
    return f'month={prev.year}-{prev.month}'


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    nxt = last + timedelta(days=1)
    return f'month={nxt.year}-{nxt.month}'


@method_decorator(login_required, name='dispatch')
class CalendarView(generic.ListView):
    model = Transacao
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month'))
        user = self.request.user

        saldos = saldos_consecutivos(user, d.year, d.month)
        atual = saldos['atual']
        proximo = saldos['proximo']
        data_prox = saldos['proximo_data']

        # ==================== CALENDÁRIO HTML ====================
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True, transacoes=atual['transacoes'])

        mes_atual_date = date(d.year, d.month, 1)
        mes_anterior_date = mes_atual_date - relativedelta(months=1)
        mes_proximo_date = mes_atual_date + relativedelta(months=1)

        context.update({
            'calendar': mark_safe(html_cal),
            'prev_month': prev_month(d),
            'next_month': next_month(d),
            'month_name': d.strftime("%B"),
            'year': d.year,
            'total_creditos': atual['creditos'],
            'total_debitos': atual['debitos'],
            'saldo_total': atual['saldo'],

            'mes_atual': mes_atual_date,
            'mes_anterior': mes_anterior_date,
            'mes_proximo': mes_proximo_date,

            'saldo_total_prox': proximo['saldo'],
            'total_creditos_prox': proximo['creditos'],
            'total_debitos_prox': proximo['debitos'],
            'mes_proximo_nome': data_prox.strftime("%B"),
        })

        return context
