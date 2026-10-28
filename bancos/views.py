from django.shortcuts import render, redirect

from .models import Rodaje
from zaq.models import Engine
from .forms import RodajeForm

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from django.core.paginator import Paginator
from django.db.models import DateField, Q
from django.utils.dateparse import parse_date
from urllib.parse import urlencode
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

# Create your views here.

CAMPOS_FECHA_FILTRO = {
    'date_analysis': ('Fecha de análisis', ''),
    'date_created': ('Fecha de registro', '__date'),
}


def create_rodaje(request):
    if request.method == 'POST':

        form = RodajeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bancos:create')

    else:
        form = RodajeForm()

    return render(
        request,
        'bancos/form.html',
        {'form': form}
    )


@require_GET
def buscar_motor(request):
    codigo = request.GET.get('codigo', '').strip()

    if not codigo:
        return JsonResponse({'encontrado': False})

    try:
        motor = (
            Engine.objects
            .select_related('category', 'operator')
            .prefetch_related('details')
            .get(code_bar=codigo)
        )
    except Engine.DoesNotExist:
        return JsonResponse({'encontrado': False})
    except Engine.MultipleObjectsReturned:
        return JsonResponse({
            'encontrado': False,
            'error': 'Código de barras duplicado'
        }, status=409)

    return JsonResponse({
        'encontrado': True,
        'motor': {
            'code_bar': motor.code_bar,
            'reference': motor.reference,
            'n_engine': motor.n_engine,
            'category': str(motor.category),
            'details': [
                str(detalle)
                for detalle in motor.details.all()
            ],
            'operator': motor.operator.get_username(),
            'date_created': motor.date_created.strftime(
                '%d/%m/%Y %H:%M'
            )
        }
    })


def summary(request):
    columnas = [
        {'nombre': 'Código de barras', 'ruta': ['engine', 'code_bar'], 'es_fecha': False},
        {'nombre': 'Referencia', 'ruta': ['engine', 'reference'], 'es_fecha': False},
        {'nombre': 'Nº motor', 'ruta': ['engine', 'n_engine'], 'es_fecha': False},
        {'nombre': 'Resultado', 'ruta': ['resultado', 'name'], 'es_fecha': False},
        {'nombre': 'Observaciones', 'ruta': ['observations'], 'es_fecha': False},
        {'nombre': 'Fecha de rodaje', 'ruta': ['date_analysis'], 'es_fecha': True},
    ]

    queryset = (
        Rodaje.objects
        .select_related('engine', 'resultado', 'operator', )
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

    return render(request, 'bancos/summary.html', {
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


class RodajeDetailView(DetailView):
    model = Rodaje
    template_name = 'bancos/detail.html'
    context_object_name = 'rodaje'

    def get_queryset(self):
        return Rodaje.objects.select_related(
            'engine'
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


class RodajeUpdateView(UpdateView):
    model = Rodaje
    form_class = RodajeForm
    template_name = 'bancos/form.html'
    context_object_name = 'bancos'

    def get_success_url(self):
        return reverse_lazy('bancos:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar rodaje #{self.object.pk}'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Rodaje actualizado correctamente.')
        return super().form_valid(form)


class RodajeDeleteView(DeleteView):
    model = Rodaje
    template_name = 'bancos/confirm_delete.html'
    context_object_name = 'bancos'
    success_url = reverse_lazy('bancos:summary')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Rodaje eliminado.')
        return super().delete(request, *args, **kwargs)
