from django.urls import path

from . import views


app_name = "gestion_forms"


urlpatterns = [
    path(
        "formulario/<int:formulario_id>/",
        views.completar_formulario,
        name="completar_formulario",
    ),

    path(
        "envio/<uuid:envio_id>/correcto/",
        views.formulario_correcto,
        name="formulario_correcto",
    ),
    path(
        "formulario/<int:formulario_id>/resultados/",
        views.resultados_formulario,
        name="resultados_formulario",
    ),
]