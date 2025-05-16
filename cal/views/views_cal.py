import calendar
from datetime import datetime, timedelta, date
from django.shortcuts import render
from django.views import generic
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ..models import Transacao
from ..utils import Calendar
from django.utils.timezone import make_aware
from django.utils.safestring import mark_safe
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum
from datetime import datetime
from dateutil.relativedelta import relativedelta

from cal.models import Transacao
# from cal.utils import Calendar, get_date, prev_month, next_month  # suas funções utilitárias
from cal.utils import Calendar


def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, 1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    return f'month={prev_month.year}-{prev_month.month}'


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    return f'month={next_month.year}-{next_month.month}'




@method_decorator(login_required, name='dispatch')
class CalendarView(generic.ListView):
    model = Transacao
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month'))  # data baseada na query string (?month=2025-05)

        # Transações do mês visualizado
        transacoes = Transacao.objects.filter(
            user=self.request.user,
            data__year=d.year,
            data__month=d.month
        )

        # Calcula o saldo para o mês exibido
        total_creditos = transacoes.filter(tipo__is_credito__iexact='1').aggregate(total=Sum('valor'))['total'] or 0
        # print(f'cal:{total_creditos}')
        total_debitos = transacoes.filter(tipo__is_credito__iexact='0').aggregate(total=Sum('valor'))['total'] or 0
        # print(total_debitos)
        saldo_total = total_creditos - total_debitos
        # print(saldo_total)

        # Calendário HTML
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True, transacoes=transacoes)

        context.update({
            'calendar': mark_safe(html_cal),
            'prev_month': prev_month(d),
            'next_month': next_month(d),
            'month_name': d.strftime("%B"),
            'year': d.year,
            'total_creditos': total_creditos,
            'total_debitos': total_debitos,
            'saldo_total': saldo_total,
        })

        return context
    

# @method_decorator(login_required, name='dispatch')
# class CalendarView(generic.ListView):
#     model = Transacao
#     template_name = 'cal/calendar.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         d = get_date(self.request.GET.get('month'))

#         transacoes = Transacao.objects.filter(
#             user=self.request.user,
#             data__year=d.year,
#             data__month=d.month
#         )

#         cal = Calendar(d.year, d.month)
#         html_cal = cal.formatmonth(withyear=True, transacoes=transacoes)

#         context.update({
#             'calendar': mark_safe(html_cal),
#             'prev_month': prev_month(d),
#             'next_month': next_month(d),
#             'month_name': d.strftime("%B"),
#             'year': d.year,
#         })
#         return context

