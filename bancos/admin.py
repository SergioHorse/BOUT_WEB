from django.contrib import admin
from django.utils import timezone
from django.utils.formats import date_format
from .models import Rodaje, EstadoRodaje

from simple_history.admin import SimpleHistoryAdmin

# Register your models here.

class MotivoRodajeFilter(admin.SimpleListFilter):
    title = 'Motivo de rodaje'
    parameter_name = 'motivo_rodaje'

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


@admin.register(EstadoRodaje)
class EstadoRetoqueAdmin(admin.ModelAdmin):
    list_display = ('name',)

    search_fields = ('name',)

    def has_module_permission(self, request):
        return (
            request.user.is_superuser or request.user.has_perm('bancos.view_estado_retoque')
        )

@admin.register(Rodaje)
class RodajeAdmin(SimpleHistoryAdmin):

    list_display = (
        'code_bar', 'reference', 'n_engine', 'show_details', 'turno','resultado', 'status', 'observations',
        'date_created', 'operator', 'date_analysis'
    )


    list_filter = ('status', 'engine__date_created', 'engine__reference', MotivoRodajeFilter,)

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

    @admin.display(description='Fecha registro')
    def date_created(self, obj):
        return date_format(obj.engine.date_created, format='DATETIME_FORMAT')

    @admin.display(description='Fecha de análisis')
    def date_analysis(self, obj):
        return date_format(obj.date_analysis, format='DATETIME_FORMAT')


    @admin.display(description='Motivo de rodaje')
    def show_details(self, obj):
        return ','.join(detail.name for detail in obj.engine.details.all())

    @admin.display(description='Turno')
    def turno(self, obj):
        return obj.engine.operator


    def save_model(self, request, obj, form, change):
        if not change:
            obj.operator = request.user

        if not obj.date_analysis:
            obj.date_analysis = timezone.now()


        if obj.resultado == 'OK':
            obj.status = EstadoRodaje.objects.get(name='Rodado ok')
        elif obj.resultado == 'NOK':
            obj.status = EstadoRodaje.objects.get(name='Rodado ok')

        super().save_model(request, obj, form, change)
