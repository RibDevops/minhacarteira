import calendar
import decimal
import locale
from datetime import date, datetime
from html import escape

from django.urls import reverse

from .models import Transacao

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except locale.Error:
        pass


def parse_mes_ano(request):
    """
    Lê 'ano' e 'mes' da querystring de forma robusta (aceita valores com
    ponto/vírgula que às vezes chegam de inputs mal formatados) e cai no
    mês/ano atual se algo vier inválido.

    Centralizado aqui porque essa lógica estava duplicada (com o mesmo
    try/except) em pelo menos 4 views diferentes — corrigir um bug ali
    exigia lembrar de corrigir nos outros 3 lugares também.
    """
    hoje = date.today()
    try:
        ano_raw = request.GET.get('ano', hoje.year)
        mes_raw = request.GET.get('mes', hoje.month)
        ano = int(float(str(ano_raw).replace('.', '').replace(',', '')))
        mes = int(float(str(mes_raw).replace('.', '').replace(',', '')))
        if not (1 <= mes <= 12):
            raise ValueError('mês fora do intervalo 1-12')
    except (ValueError, TypeError):
        ano, mes = hoje.year, hoje.month
    return ano, mes


def intervalo_do_mes(ano, mes):
    """
    Retorna (data_inicio, data_fim) como objetos `date` puros (sem hora/
    timezone) para filtrar um DateField com data__gte / data__lt.

    Importante: Transacao.data é um DateField, não DateTimeField. Usar
    make_aware(datetime(...)) para filtrar um DateField mistura um
    datetime "aware" (com timezone) numa comparação que não tem hora,
    o que pode deslocar o dia 1 do mês para o mês errado dependendo do
    TIME_ZONE do projeto. Comparar date com date evita essa ambiguidade.
    """
    from dateutil.relativedelta import relativedelta
    data_inicio = date(ano, mes, 1)
    data_fim = data_inicio + relativedelta(months=1)
    return data_inicio, data_fim


def gerar_transacoes_pendentes(user):
    """
    Gera as transações "faltando" de cada Recorrência ativa do usuário
    (assinaturas, aluguel, etc).

    Chamada a cada request autenticado (via context_processors.saldos_mensais),
    então não depende de Celery/cron: se o usuário não abre o app por 2 meses,
    ao voltar ele vê os lançamentos retroativos gerados na hora.

    Limita o backfill a 3 meses atrás para não criar uma avalanche de
    transações se uma recorrência antiga ficar "esquecida" por muito tempo.
    """
    from dateutil.relativedelta import relativedelta
    from .models import Recorrencia, Transacao

    hoje = date.today()
    limite_backfill = (hoje.replace(day=1) - relativedelta(months=3))

    recorrencias = Recorrencia.objects.filter(
        user=user, ativa=True
    ).select_related('tipo', 'categoria', 'cartao')

    for r in recorrencias:
        inicio = r.data_inicio or r.created_at.date()
        mes_cursor = max(inicio.replace(day=1), limite_backfill)
        fim = r.data_fim or hoje

        while mes_cursor <= fim and mes_cursor <= hoje.replace(day=1):
            dia = min(r.dia_cobranca, calendar.monthrange(mes_cursor.year, mes_cursor.month)[1])
            data_lancamento = date(mes_cursor.year, mes_cursor.month, dia)

            ja_existe = Transacao.objects.filter(
                recorrencia=r,
                data__year=mes_cursor.year,
                data__month=mes_cursor.month,
            ).exists()

            if not ja_existe and data_lancamento <= hoje:
                Transacao.objects.create(
                    user=user,
                    tipo=r.tipo,
                    categoria=r.categoria,
                    cartao=r.cartao,
                    titulo=r.titulo,
                    valor=r.valor,
                    data=data_lancamento,
                    parcelas=1,
                    observacoes=r.observacoes,
                    recorrencia=r,
                )

            mes_cursor = mes_cursor + relativedelta(months=1)


class Calendar(calendar.HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super().__init__()

    def formatday(self, day, transacoes):
        """
        Renderiza um único dia do calendário. Versão única (a anterior
        tinha duas definições conflitantes desta função — a segunda
        sobrescrevia a primeira silenciosamente).
        """
        transacoes_do_dia = transacoes.filter(data__day=day)

        itens = []
        for t in transacoes_do_dia:
            try:
                valor = t.valor if isinstance(t.valor, (int, float, decimal.Decimal)) else decimal.Decimal(str(t.valor))
                # Escape do título para evitar XSS
                titulo_seguro = escape(t.titulo)
                item = f'<li><a href="{t.get_absolute_url()}">{titulo_seguro} - R$ {valor:.2f}</a></li>'
            except (TypeError, ValueError, decimal.InvalidOperation):
                titulo_seguro = escape(t.titulo)
                item = f'<li><a href="{t.get_absolute_url()}">{titulo_seguro} - CC</a></li>'
            itens.append(item)

        itens_html = ''.join(itens)

        if day != 0:
            css_class = 'today' if date(self.year, self.month, day) == datetime.today().date() else ''
            return f'<td class="{css_class}"><span class="date">{day}</span><ul>{itens_html}</ul></td>'
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
