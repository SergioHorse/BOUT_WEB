from .models import Formulario


def formularios_disponibles(request):
    formularios = Formulario.objects.filter(
        activo=True,
    ).order_by("nombre")

    return {
        "formularios_disponibles": formularios,
    }