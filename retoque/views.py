from urllib.parse import urlencode

from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.core.paginator import Paginator
from django.db.models import DateField, Q
from django.utils.dateparse import parse_date
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .forms import RetoqueForm
from .models import CampoListado, Retoque


# Campos por los que se puede filtrar por rango de fechas: clave -> (etiqueta, sufijo de lookup)
CAMPOS_FECHA_FILTRO = {
    'date_analysis': ('Fecha de análisis', ''),
    'date_created': ('Fecha de registro', '__date'),
}


def _columnas_visibles():
    """Devuelve las columnas del listado definidas en CampoListado (soporta rutas con __)."""
    columnas = []

    for config in CampoListado.objects.filter(visible=True).order_by('orden', 'id'):
        partes = config.campo.split('__')
        modelo_actual = Retoque
        campo = None

        try:
            for indice, parte in enumerate(partes):
                campo = modelo_actual._meta.get_field(parte)
                if indice < len(partes) - 1:
                    if not campo.is_relation or campo.related_model is None:
                        raise FieldDoesNotExist(parte)
                    modelo_actual = campo.related_model
        except FieldDoesNotExist:
            continue

        columnas.append({
            'titulo': config.titulo,
            'ruta': partes,
            'es_fecha': isinstance(campo, DateField),
        })

    return columnas


def summary(request):
    columnas = _columnas_visibles()

    queryset = (
        Retoque.objects
        .select_related('engine', 'status', 'operator', 'allocation_retouching_cost')
        .order_by('-pk')
    )

    # Buscador: texto libre sobre los campos visibles del listado (excepto fechas)
    q = request.GET.get('q', '').strip()
    if q:
        condicion = Q()
        for columna in columnas:
            if not columna['es_fecha']:
                condicion |= Q(**{'__'.join(columna['ruta']) + '__icontains': q})
        queryset = queryset.filter(condicion)

    # Rango de fechas (desde / hasta) sobre el campo elegido
    campo_fecha = request.GET.get('campo_fecha', 'date_analysis')
    if campo_fecha not in CAMPOS_FECHA_FILTRO:
        campo_fecha = 'date_analysis'
    _, sufijo = CAMPOS_FECHA_FILTRO[campo_fecha]

    fecha_desde_txt = request.GET.get('fecha_desde', '')
    fecha_hasta_txt = request.GET.get('fecha_hasta', '')
    fecha_desde = parse_date(fecha_desde_txt) if fecha_desde_txt else None
    fecha_hasta = parse_date(fecha_hasta_txt) if fecha_hasta_txt else None

    if fecha_desde:
        queryset = queryset.filter(**{f'{campo_fecha}{sufijo}__gte': fecha_desde})
    if fecha_hasta:
        queryset = queryset.filter(**{f'{campo_fecha}{sufijo}__lte': fecha_hasta})

    page_obj = Paginator(queryset, 10).get_page(request.GET.get('page'))

    filas = []
    for retouch in page_obj:
        celdas = []
        for columna in columnas:
            valor = retouch
            for parte in columna['ruta']:
                if valor is None:
                    break
                valor = getattr(valor, parte, None)
            celdas.append({'valor': valor, 'es_fecha': columna['es_fecha']})

        filas.append({'pk': retouch.pk, 'celdas': celdas})

    filtros_qs = urlencode({
        'q': q,
        'campo_fecha': campo_fecha,
        'fecha_desde': fecha_desde_txt,
        'fecha_hasta': fecha_hasta_txt,
    })

    return render(request, 'retoque/summary.html', {
        'columnas': columnas,
        'filas': filas,
        'page_obj': page_obj,
        'q': q,
        'campo_fecha': campo_fecha,
        'fecha_desde': fecha_desde_txt,
        'fecha_hasta': fecha_hasta_txt,
        'opciones_fecha': [(clave, etiqueta) for clave, (etiqueta, _) in CAMPOS_FECHA_FILTRO.items()],
        'filtros_qs': filtros_qs,
    })


class RetoqueDetailView(DetailView):
    model = Retoque
    template_name = 'retoque/detail.html'
    context_object_name = 'retoque'

    def get_queryset(self):
        return Retoque.objects.select_related(
            'engine', 'status', 'operator', 'allocation_retouching_cost'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campos = []

        motor = self.object.engine
        if motor is not None:
            for campo in motor._meta.concrete_fields:
                if campo.primary_key:
                    continue
                campos.append({
                    'clave': campo.verbose_name,
                    'valor': getattr(motor, campo.name),
                })

        for campo in self.object._meta.concrete_fields:
            if campo.name == 'engine' or campo.primary_key or campo.name == 'date_created':
                continue

            valor = getattr(self.object, campo.name)
            if campo.choices:
                valor = getattr(self.object, f'get_{campo.name}_display')()

            campos.append({'clave': campo.verbose_name, 'valor': valor})

        context['campos'] = campos
        return context


class RetoqueCreateView(CreateView):
    model = Retoque
    form_class = RetoqueForm
    template_name = 'retoque/form.html'
    success_url = reverse_lazy('retoque:summary')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo retoque'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Retoque creado correctamente.')
        return super().form_valid(form)


class RetoqueUpdateView(UpdateView):
    model = Retoque
    form_class = RetoqueForm
    template_name = 'retoque/form.html'
    context_object_name = 'retoque'

    def get_success_url(self):
        return reverse_lazy('retoque:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar retoque #{self.object.pk}'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Retoque actualizado correctamente.')
        return super().form_valid(form)


class RetoqueDeleteView(DeleteView):
    model = Retoque
    template_name = 'retoque/confirm_delete.html'
    context_object_name = 'retoque'
    success_url = reverse_lazy('retoque:summary')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Retoque eliminado.')
        return super().delete(request, *args, **kwargs)


