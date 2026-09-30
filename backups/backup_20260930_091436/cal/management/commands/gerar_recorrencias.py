from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction

from cal.models import Recorrencia, Transacao
from cal.utils import gerar_transacoes_pendentes


class Command(BaseCommand):
    help = "Gera transações pendentes de todas as recorrências ativas (para ser rodado 1x/dia via cron)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="Gerar apenas para um usuário específico",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra o que seria criado sem salvar",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        dry_run = options["dry_run"]

        if user_id:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(pk=user_id)
                self.stdout.write(f"Gerando para usuário: {user.username}")
                criadas = self._processar_usuario(user, dry_run)
                self.stdout.write(self.style.SUCCESS(f"Transações criadas: {criadas}"))
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Usuário {user_id} não encontrado"))
        else:
            from django.contrib.auth.models import User
            total = 0
            for user in User.objects.filter(is_active=True):
                criadas = self._processar_usuario(user, dry_run)
                total += criadas
            self.stdout.write(self.style.SUCCESS(f"Total transações criadas: {total}"))

    def _processar_usuario(self, user, dry_run):
        """Versão síncrona e atômica do gerar_transacoes_pendentes"""
        from dateutil.relativedelta import relativedelta
        import calendar

        hoje = date.today()
        limite_backfill = (hoje.replace(day=1) - relativedelta(months=3))

        recorrencias = Recorrencia.objects.filter(
            user=user, ativa=True
        ).select_related("tipo", "categoria", "cartao")

        criadas = 0
        for r in recorrencias:
            inicio = r.data_inicio or r.created_at.date()
            mes_cursor = max(inicio.replace(day=1), limite_backfill)
            fim = r.data_fim or hoje

            while mes_cursor <= fim and mes_cursor <= hoje.replace(day=1):
                dia = min(r.dia_cobranca, calendar.monthrange(mes_cursor.year, mes_cursor.month)[1])
                data_lancamento = date(mes_cursor.year, mes_cursor.month, dia)

                if data_lancamento > hoje:
                    break

                ja_existe = Transacao.objects.filter(
                    recorrencia=r,
                    data__year=mes_cursor.year,
                    data__month=mes_cursor.month,
                ).exists()

                if not ja_existe:
                    if not dry_run:
                        with transaction.atomic():
                            # double-check dentro da transação
                            if not Transacao.objects.filter(
                                recorrencia=r,
                                data__year=mes_cursor.year,
                                data__month=mes_cursor.month,
                            ).exists():
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
                                criadas += 1
                    else:
                        criadas += 1
                        self.stdout.write(f"  [DRY-RUN] {user.username}: {r.titulo} - {data_lancamento}")

                mes_cursor = mes_cursor + relativedelta(months=1)

        return criadas