import uuid
from datetime import date, timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.utils.decorators import method_decorator

from ..forms import CartaoForm, CategoriaForm, MetaCategoriaForm, RecorrenciaForm, TransacaoForm
from ..models import Cartao, Categoria, MetaCategoria, Recorrencia, Transacao, Tipo
from ..services import calcular_proxima_fatura, consumo_por_cartao, resumo_categorias_e_tipos
from ..utils import intervalo_do_mes, parse_mes_ano

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


class UserOwnsObjectMixin:
    """Mixin para garantir que o objeto pertence ao usuário logado."""
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


# ======================================================
# TRANSAÇÃO - CBVs
# ======================================================

class TransacaoListView(LoginRequiredMixin, UserOwnsObjectMixin, ListView):
    model = Transacao
    template_name = 'cal/lista_transacoes.html'
    context_object_name = 'transacoes'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        ano, mes = parse_mes_ano(self.request)
        data_inicio, data_fim = intervalo_do_mes(ano, mes)
        qs = qs.filter(data__gte=data_inicio, data__lt=data_fim).select_related('tipo', 'categoria', 'cartao').order_by('-data')

        tipo_filtro = self.request.GET.get('tipo')
        categoria_filtro = self.request.GET.get('categoria')
        if tipo_filtro:
            qs = qs.filter(tipo_id=tipo_filtro)
        if categoria_filtro:
            qs = qs.filter(categoria_id=categoria_filtro)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ano, mes = parse_mes_ano(self.request)
        hoje = date.today()
        data_atual = date(ano, mes, 1)

        transacoes = self.get_queryset()
        total_creditos = transacoes.filter(tipo__codigo='C').aggregate(Sum('valor'))['valor__sum'] or 0
        total_debitos = transacoes.filter(tipo__codigo='D').aggregate(Sum('valor'))['valor__sum'] or 0

        ctx.update({
            'tipos': Tipo.objects.all(),
            'categorias': Categoria.get_for_user(self.request.user),
            'mes_atual': data_atual,
            'mes_anterior': data_atual - relativedelta(months=1),
            'mes_proximo': data_atual + relativedelta(months=1),
            'saldo_total': total_creditos - total_debitos,
        })
        return ctx


class TransacaoCreateView(LoginRequiredMixin, CreateView):
    model = Transacao
    form_class = TransacaoForm
    template_name = 'cal/transacao_form.html'
    success_url = reverse_lazy('cal:transacoes_mes')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        # Normaliza o valor (aceita vírgula decimal) antes do form validar
        if 'valor' in request.POST:
            post = request.POST.copy()
            post['valor'] = post['valor'].replace('.', '').replace(',', '.')
            request.POST = post
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        transacao = form.save(commit=False)
        transacao.user = self.request.user

        tipo = transacao.tipo
        categoria = transacao.categoria
        data = transacao.data
        parcelas = int(form.cleaned_data.get('parcelas') or 1)

        valor_total = transacao.valor or Decimal('0')
        valor_parcela = valor_total.quantize(Decimal("0.01"))
        grupo_id = str(uuid.uuid4()) if parcelas > 1 else None

        data_base_parcela = data
        if transacao.cartao:
            data_base_parcela = calcular_proxima_fatura(data)

        for i in range(parcelas):
            data_final_parcela = data_base_parcela + relativedelta(months=i)

            Transacao.objects.create(
                user=self.request.user,
                tipo=tipo,
                cartao=transacao.cartao,
                categoria=categoria,
                titulo=f"{transacao.titulo} ({i + 1}/{parcelas})" if parcelas > 1 else transacao.titulo,
                valor=valor_parcela,
                data=data_final_parcela,
                parcelas=parcelas,
                data_fim=data_base_parcela + relativedelta(months=parcelas - 1),
                observacoes=transacao.observacoes,
                grupo_id=grupo_id
            )

        messages.success(self.request, 'Transação criada com sucesso!')
        return redirect(self.success_url)


class TransacaoUpdateView(LoginRequiredMixin, UserOwnsObjectMixin, UpdateView):
    model = Transacao
    form_class = TransacaoForm
    template_name = 'cal/transacao_form.html'
    success_url = reverse_lazy('cal:transacoes_mes')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Transação atualizada com sucesso!')
        return super().form_valid(form)


class TransacaoDeleteView(LoginRequiredMixin, UserOwnsObjectMixin, DeleteView):
    """
    Exclui uma transação. Suporta dois fluxos distintos:

    - POST com `excluir_proximas=true` (e `grupo_id` presente): exclui em
      cascata todas as parcelas do mesmo grupo com data >= a transação
      atual. Usado pelo modal de "excluir esta e futuras" no template.
    - POST simples: exclui apenas a transação (mantém irmãs do grupo).
    - GET: renderiza confirmação (fallback para o template que ainda use
      <form method="post"> sem JS).

    Compatível com chamada AJAX (Fetch): retorna JsonResponse quando o
    cabeçalho `x-requested-with: XMLHttpRequest` estiver presente.
    """
    model = Transacao
    template_name = 'cal/confirmar_exclusao.html'
    success_url = reverse_lazy('cal:transacoes_mes')

    def get_queryset(self):
        return Transacao.objects.filter(user=self.request.user)

    def form_valid(self, form):
        """Substitui o fluxo padrão de DeleteView (que só chama self.object.delete()).
        
        Implementa a lógica de exclusão em cascata via `excluir_proximas`.
        """
        self.object = self.get_object()
        excluir_proximas = self.request.POST.get('excluir_proximas') == 'true'

        if excluir_proximas and self.object.grupo_id:
            Transacao.objects.filter(
                user=self.request.user,
                grupo_id=self.object.grupo_id,
                data__gte=self.object.data,
            ).delete()
        else:
            self.object.delete()

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Transação excluída com sucesso!'})

        messages.success(self.request, 'Transação excluída com sucesso!')
        return redirect(self.success_url)


# ======================================================
# CARTÃO - CBVs
# ======================================================

class CartaoListView(LoginRequiredMixin, UserOwnsObjectMixin, ListView):
    model = Cartao
    template_name = 'cal/cartoes_resumo.html'
    context_object_name = 'cartoes'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ano, mes = parse_mes_ano(self.request)
        data_atual = date(ano, mes, 1)

        dados = consumo_por_cartao(self.request.user, ano, mes)
        ctx.update({
            'labels': dados['labels'],
            'consumo': dados['consumo'],
            'limites': dados['limites'],
            'mes_atual': data_atual,
            'mes_anterior': data_atual - relativedelta(months=1),
            'mes_proximo': data_atual + relativedelta(months=1),
        })
        return ctx


class CartaoCreateView(LoginRequiredMixin, CreateView):
    model = Cartao
    form_class = CartaoForm
    template_name = 'cal/cartao_form.html'
    success_url = reverse_lazy('cal:cartoes_resumo')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Cartão adicionado com sucesso!')
        return super().form_valid(form)


class CartaoUpdateView(LoginRequiredMixin, UserOwnsObjectMixin, UpdateView):
    model = Cartao
    form_class = CartaoForm
    template_name = 'cal/cartao_form.html'
    success_url = reverse_lazy('cal:cartoes_resumo')

    def form_valid(self, form):
        messages.success(self.request, 'Cartão atualizado com sucesso!')
        return super().form_valid(form)


class CartaoDeleteView(LoginRequiredMixin, UserOwnsObjectMixin, DeleteView):
    model = Cartao
    template_name = 'cal/confirmar_exclusao.html'
    success_url = reverse_lazy('cal:cartoes_resumo')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cartão excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# ======================================================
# CATEGORIA - CBVs
# ======================================================

class CategoriaListView(LoginRequiredMixin, UserOwnsObjectMixin, ListView):
    model = Categoria
    template_name = 'cal/categoria_list.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).order_by('nome')


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'cal/categoria_form.html'
    success_url = reverse_lazy('cal:categorias')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)


class CategoriaUpdateView(LoginRequiredMixin, UserOwnsObjectMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'cal/categoria_form.html'
    success_url = reverse_lazy('cal:categorias')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)


class CategoriaDeleteView(LoginRequiredMixin, UserOwnsObjectMixin, DeleteView):
    model = Categoria
    template_name = 'cal/confirmar_exclusao.html'
    success_url = reverse_lazy('cal:categorias')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Categoria excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# ======================================================
# META CATEGORIA - CBVs
# ======================================================

class MetaCategoriaListView(LoginRequiredMixin, UserOwnsObjectMixin, ListView):
    model = MetaCategoria
    template_name = 'cal/metas_dashboard.html'
    context_object_name = 'metas'

    def get_queryset(self):
        ano, mes = parse_mes_ano(self.request)
        return MetaCategoria.objects.filter(user=self.request.user, mes=mes, ano=ano)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ano, mes = parse_mes_ano(self.request)
        data_atual = date(ano, mes, 1)
        mes_anterior = (data_atual - timedelta(days=1)).replace(day=1)
        mes_proximo = (data_atual + timedelta(days=31)).replace(day=1)

        categorias_labels = []
        categorias_valores = []
        dados = []

        for meta in ctx['metas']:
            transacoes = Transacao.objects.filter(
                user=self.request.user,
                categoria=meta.categoria,
                data__year=ano,
                data__month=mes,
            ).select_related('tipo').order_by('-data')

            gasto = sum((t.valor_decimal for t in transacoes), Decimal('0'))
            limite = float(meta.limite) if meta.limite else 0
            restante = max(limite - float(gasto), 0)

            percentual = round((float(gasto) / limite) * 100, 2) if limite else 0
            percentual = min(percentual, 100)

            if percentual < 70:
                status = 'success'
            elif percentual < 100:
                status = 'warning'
            else:
                status = 'danger'

            categorias_labels.append(meta.categoria.nome)
            categorias_valores.append(float(gasto))

            dados.append({
                'id': meta.id,
                'categoria': meta.categoria.nome,
                'limite': meta.limite,
                'gasto': gasto,
                'restante': restante,
                'percentual': percentual,
                'status': status,
                'transacoes': transacoes,
            })

        ctx.update({
            'dados': dados,
            'mes': mes,
            'ano': ano,
            'mes_atual': f"{MESES_PT[mes]} de {ano}",
            'meses': MESES_PT,
            'mes_anterior': mes_anterior,
            'mes_proximo': mes_proximo,
            'grafico_labels': categorias_labels,
            'grafico_valores': categorias_valores,
        })
        return ctx


class MetaCategoriaCreateView(LoginRequiredMixin, CreateView):
    model = MetaCategoria
    form_class = MetaCategoriaForm
    template_name = 'cal/meta_form.html'
    success_url = reverse_lazy('cal:metas_categoria')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.mes = form.cleaned_data['mes']
        form.instance.ano = form.cleaned_data['ano']
        form.instance.limite = form.cleaned_data['limite']
        messages.success(self.request, 'Meta cadastrada com sucesso!')
        return super().form_valid(form)


class MetaCategoriaUpdateView(LoginRequiredMixin, UserOwnsObjectMixin, UpdateView):
    model = MetaCategoria
    form_class = MetaCategoriaForm
    template_name = 'cal/meta_form.html'
    success_url = reverse_lazy('cal:metas_categoria')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['mes_ano'] = f"{self.object.mes:02d}-{self.object.ano}"
        initial['limite'] = self.object.limite
        return initial

    def form_valid(self, form):
        form.instance.limite = form.cleaned_data['limite']
        messages.success(self.request, 'Meta atualizada com sucesso!')
        return super().form_valid(form)


class MetaCategoriaDeleteView(LoginRequiredMixin, UserOwnsObjectMixin, DeleteView):
    model = MetaCategoria
    template_name = 'cal/confirmar_exclusao_meta.html'
    success_url = reverse_lazy('cal:metas_categoria')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Meta excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# ======================================================
# RECORRÊNCIA - CBVs
# ======================================================

class RecorrenciaListView(LoginRequiredMixin, UserOwnsObjectMixin, ListView):
    model = Recorrencia
    template_name = 'cal/recorrencia_listar.html'
    context_object_name = 'recorrencias'


class RecorrenciaCreateView(LoginRequiredMixin, CreateView):
    model = Recorrencia
    form_class = RecorrenciaForm
    template_name = 'cal/recorrencia_form.html'
    success_url = reverse_lazy('cal:recorrencia_listar')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Recorrência criada com sucesso!')
        return super().form_valid(form)


class RecorrenciaUpdateView(LoginRequiredMixin, UserOwnsObjectMixin, UpdateView):
    model = Recorrencia
    form_class = RecorrenciaForm
    template_name = 'cal/recorrencia_form.html'
    success_url = reverse_lazy('cal:recorrencia_listar')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Recorrência atualizada com sucesso!')
        return super().form_valid(form)


class RecorrenciaDeleteView(LoginRequiredMixin, UserOwnsObjectMixin, DeleteView):
    model = Recorrencia
    template_name = 'cal/confirmar_exclusao.html'
    success_url = reverse_lazy('cal:recorrencia_listar')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Recorrência excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


class RecorrenciaToggleStatusView(LoginRequiredMixin, UserOwnsObjectMixin, DetailView):
    model = Recorrencia

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.ativa = not self.object.ativa
        self.object.save()
        status = "ativada" if self.object.ativa else "desativada"
        messages.success(request, f'Recorrência {status} com sucesso!')
        return redirect('cal:recorrencia_listar')


# ======================================================
# TIPO - CBVs (Staff only)
# ======================================================

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class TipoListView(LoginRequiredMixin, ListView):
    model = Tipo
    template_name = 'cal/tipo_list.html'
    context_object_name = 'tipos'


class TipoCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Tipo
    fields = ['codigo', 'descricao']
    template_name = 'cal/tipo_form.html'
    success_url = reverse_lazy('cal:tipo_list')


class TipoUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Tipo
    fields = ['codigo', 'descricao']
    template_name = 'cal/tipo_form.html'
    success_url = reverse_lazy('cal:tipo_list')


class TipoDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Tipo
    template_name = 'cal/tipo_confirm_delete.html'
    success_url = reverse_lazy('cal:tipo_list')