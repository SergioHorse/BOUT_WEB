from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import FieldDoesNotExist
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q, DateField
from .models import Retoque, CampoListado
from .forms import RetoqueForm


# Create your views here.

def summary(request):

    configuracion = CampoListado.objects.filter(
        visible=True
    ).order_by('orden', 'id')

    columnas = []

    for config in configuracion:

        modelo_actual = Retoque
        partes = config.campo.split('__')

        try:
            for indice, parte in enumerate(partes):
                campo = modelo_actual._meta.get_field(parte)

                if indice < len(partes)-1:
                    if not campo.is_relation or campo.related_model is None:
                        raise FieldDoesNotExist(parte)
                    modelo_actual = campo.related_model

            config.es_fecha = isinstance(campo, DateField)
            columnas.append(config)

        except FieldDoesNotExist:
            continue


    retouches = Retoque.objects.all()

    paginator = Paginator(retouches.order_by('-pk'), 10)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)


    filas = []

    # for retouch in retouches:
    for retouch in page_obj:

        valores = []

        for columna in columnas:

            valor = retouch

            for parte in columna.campo.split('__'):
                if valor is None:
                    break
                valor = getattr(valor, parte, None)

            valores.append(valor)

        filas.append({
            'pk':retouch.pk,
            'valores': valores,
        })

    return render(
        request,
        'retoque/summary.html',
        {
            'columnas': columnas,
            'filas': filas,
            'page_obj': page_obj,
        }
    )


class RetoqueDetailView(DetailView):

    model = Retoque
    template_name = 'retoque/detail.html'
    context_object_name = 'retoque'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        campos = []


        motor = self.object.engine

        if motor is not None:
            for campo in motor._meta.concrete_fields:
                if campo.primary_key:
                    continue


                campos.append(
                    {'clave': campo.verbose_name,
                     'valor': getattr(motor, campo.name)}
                )

        for campo in self.object._meta.concrete_fields:


            if campo.name == 'engine' or campo.primary_key or campo.name == 'date_created':
                continue

            valor = getattr(self.object, campo.name)

            if campo.choices:
                valor = getattr(self.object, f'get_{campo.name}_display')()

            campos.append(
                {'clave': campo.verbose_name,
                 'valor': valor}
            )


        context['campos'] = campos
        return context


def edit_retouch(request, pk):

    retouch = get_object_or_404(Retoque, pk=pk)

    if request.method == 'POST':
        form = RetoqueForm(request.POST, instance=retouch)

        if form.is_valid():
            form.save()
            return redirect('/retoques')

    else:
        form = RetoqueForm(instance=retouch)

    return render(
        request,
        'retoque/edit.html',
        {'form': form,
         'retouch': retouch}
    )










