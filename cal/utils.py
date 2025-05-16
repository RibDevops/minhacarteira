  
import calendar
from datetime import date, datetime

from django.urls import reverse
from .models import Transacao
import locale


locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

class Calendar(calendar.HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super().__init__()

    def formatday(self, day, transacoes):
        transacoes_do_dia = transacoes.filter(data__day=day)
        # itens = ''.join(f'<li>{t.get_html_url}</li>' for t in transacoes_do_dia)
        # itens = ''.join(f'<li>{t.titulo}</li>' for t in transacoes_do_dia)
        itens = ''.join(f'<li><a href="{t.get_absolute_url()}">{t.titulo} - R$ {t.valor}</a></li>' for t in transacoes_do_dia)

        if day != 0:
            css_class = 'today' if date(self.year, self.month, day) == datetime.today().date() else ''
            return f'<td class="{css_class}"><span class="date">{day}</span><ul>{itens}</ul></td>'
        return '<td></td>'

    def formatweek(self, theweek, transacoes):
        return '<tr>' + ''.join(self.formatday(d, transacoes) for d, _ in theweek) + '</tr>'

    def formatweekheader(self):
        dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        return '<tr>' + ''.join(f'<th>{dia}</th>' for dia in dias) + '</tr>'

    def formatmonth(self, withyear=True, transacoes=None):
        if transacoes is None:
            transacoes = Transacao.objects.none()

        cal = '<table class="calendar">\n'
        cal += self.formatmonthname(self.year, self.month, withyear=withyear)
        cal += self.formatweekheader()
        for week in self.monthdays2calendar(self.year, self.month):
            cal += self.formatweek(week, transacoes)
        cal += '</table>'
        return cal

    def formatmonthname(self, theyear, themonth, withyear=True):
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        nome_mes = meses[themonth - 1]
        return f'<tr><th colspan="7" class="month">{nome_mes} {theyear if withyear else ""}</th></tr>'

