from django.contrib import admin
from django import forms as django_forms
from .models import Retoque, EstadoRetoque, ImputacionRetoque, CampoListado
from zaq.models import Engine

from simple_history.admin import SimpleHistoryAdmin

# Register your models here.

admin.site.site_header = 'HORSE | WEB'
admin.site.site_title = 'HORSE | WEB'
admin.site.index_title = 'Panel de administrador'


class MotivoRetoqueFilter(admin.SimpleListFilter):
    title = 'Motivo de retoque'
    parameter_name = 'motivo_retoque'

    def lookups(self, request, model_admin):
        motivos = (
            model_admin.model.objects
            .values_list(
                'engine__details__name',
                flat=True,
            )
            .exclude(engine__details__name__isnull=True)
            .distinct()
            .order_by('engine__details__name')
        )

        return [(motivo, motivo) for motivo in sorted(motivos) if motivo]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(engine__details__name=self.value()).distinct()

        return queryset


@admin.register(EstadoRetoque)
class EstadoRetoqueAdmin(admin.ModelAdmin):
    list_display = ('name',)

    search_fields = ('name',)


@admin.register(ImputacionRetoque)
class ImputacionRetoqueAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Retoque)
class RetoqueAdmin(SimpleHistoryAdmin):



    list_display = (
        'code_bar', 'reference', 'n_engine', 'show_details', 'status', 'observations',
        'date_created', 'operator', 'date_analysis', 'allocation_retouching_cost'
    )

    list_filter = ('status', 'engine__date_created', 'engine__reference', MotivoRetoqueFilter,)

    search_fields = ('engine__code_bar', 'engine__reference', 'engine__n_engine',)

    readonly_fields = ('date_created', 'date_analysis', 'operator', 'status', )

    list_per_page = 20

    @admin.display(description='Código de barras')
    def code_bar(self, obj):
        return obj.engine.code_bar

    @admin.display(description='Referencia')
    def reference(self, obj):
        return obj.engine.reference

    @admin.display(description='Nº motor')
    def n_engine(self, obj):
        return obj.engine.n_engine

    @admin.display(description='Motivo de retoque')
    def show_details(self, obj):
        return ','.join(detail.name for detail in obj.engine.details.all())

    def save_model(self, request, obj, form, change):
        if not change:
            obj.operator = request.user

        super().save_model(request, obj, form, change)


def obtener_opciones_campos(modelo, prefijo='', nivel=0):
    opciones_campos = []

    for campo in (list(modelo._meta.fields)+ list(modelo._meta.many_to_many)):
        nombre = f'{prefijo}{campo.name}'
        titulo = str(campo.verbose_name).capitalize()

        if campo.is_relation and campo.related_model:
            if nivel < 1:
                opciones_campos.extend(
                    obtener_opciones_campos(
                        campo.related_model,
                        prefijo=f'{nombre}__',
                        nivel=nivel + 1
                    )
                )
        else:
            opciones_campos.append((nombre,
                                    f'{titulo} ({nombre})'))

    return opciones_campos


class CampoListadoForm(django_forms.ModelForm):
    campo = django_forms.ChoiceField(
        label='Campo',
        choices=[]
    )

    class Meta:
        model = CampoListado
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['campo'].choices = [
                                           ('', 'Seleccionar campo')
                                       ] + obtener_opciones_campos(Retoque) + [
            ('details_engine', 'Detalles seleccionados'),
        ]


@admin.register(CampoListado)
class CampoListadoAdmin(admin.ModelAdmin):
    form = CampoListadoForm

    list_display = (
        'campo',
        'titulo',
        'visible',
        'orden',
    )

    list_editable = (
        'titulo',
        'visible',
        'orden',
    )

    ordering = (
        'campo',
        'id'
    )

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser and request.user.is_active

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser and request.user.is_active

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.user.is_active

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser and request.user.is_active

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser and request.user.is_active
