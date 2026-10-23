from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilter
from .models import Engine, Detail, Category

from simple_history.admin import SimpleHistoryAdmin

# Register your models here.


class MotivoZaqFilter(admin.SimpleListFilter):
    title = 'Detalles fallo'
    parameter_name = 'motivo_retirada'

    def lookups(self, request, model_admin):
        motivos = (
            model_admin.model.objects
            .values_list(
                'details__name',
                flat=True,
            )
            .exclude(details__name__isnull=True)
            .distinct()
            .order_by('details__name')
        )


        return [(motivo, motivo) for motivo in sorted(motivos) if motivo]

    def queryset(self, request, queryset):

        if self.value():
            return queryset.filter(details__name=self.value()).distinct()

        return queryset

class DetailCategory(admin.TabularInline):
    """
    Detalles dentro de cada categoría
    """
    model = Detail
    extra = 1
    fields = ('name', 'active', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Categorías
    """
    list_display = ('name', 'color', 'active', 'order', 'icon')
    list_editable = ('active', 'order')
    search_fields = ('name', )
    ordering = ('order', 'name')

    inlines = [DetailCategory]

    list_per_page = 20

@admin.register(Engine)
class EngineAdmin(SimpleHistoryAdmin):
    """
    Motor
    """
    list_display = ('code_bar','reference', 'n_engine', 'category', 'show_details',
                   'operator', 'date_created')
    list_filter = ('category', ('date_created', DateTimeRangeFilter), 'reference', MotivoZaqFilter)
    search_fields = ('code_bar', )
    readonly_fields = ('date_created',)
    filter_horizontal = ('details',)

    list_per_page = 20

    @admin.display(description='Fallos/Retoques')
    def show_details(self, obj):
        return ','.join(detail.name for detail in obj.details.all())












