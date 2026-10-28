from django import forms


class FormularioDinamico(forms.Form):

    def __init__(self, *args, formulario, **kwargs):
        super().__init__(*args, **kwargs)

        preguntas = formulario.preguntas.filter(
            activa=True
        ).prefetch_related("opciones").order_by("orden", "id")

        for pregunta in preguntas:
            nombre_campo = f"pregunta_{pregunta.id}"

            argumentos = {
                "label": pregunta.texto,
                "required": pregunta.obligatoria,
            }

            if pregunta.tipo_respuesta == pregunta.TipoRespuesta.TEXTO:
                campo = forms.CharField(
                    **argumentos,
                    widget=forms.TextInput(
                        attrs={
                            "class": "form-control",
                        }
                    ),
                )

            elif pregunta.tipo_respuesta == pregunta.TipoRespuesta.TEXTO_LARGO:
                campo = forms.CharField(
                    **argumentos,
                    widget=forms.Textarea(
                        attrs={
                            "class": "form-control",
                            "rows": 4,
                        }
                    ),
                )

            elif pregunta.tipo_respuesta == pregunta.TipoRespuesta.BINARIO:
                campo = forms.ChoiceField(
                    **argumentos,
                    choices=[
                        ("si", "Sí"),
                        ("no", "No"),
                    ],
                    widget=forms.RadioSelect,
                )

            elif pregunta.tipo_respuesta == pregunta.TipoRespuesta.OPCION_UNICA:
                opciones = [
                    (opcion.id, opcion.texto)
                    for opcion in pregunta.opciones.all()
                ]

                campo = forms.ChoiceField(
                    **argumentos,
                    choices=opciones,
                    widget=forms.RadioSelect,
                )

            elif pregunta.tipo_respuesta == pregunta.TipoRespuesta.OPCION_MULTIPLE:
                opciones = [
                    (opcion.id, opcion.texto)
                    for opcion in pregunta.opciones.all()
                ]

                campo = forms.MultipleChoiceField(
                    **argumentos,
                    choices=opciones,
                    widget=forms.CheckboxSelectMultiple,
                )

            elif pregunta.tipo_respuesta == pregunta.TipoRespuesta.NUMERO:
                campo = forms.DecimalField(
                    **argumentos,
                    widget=forms.NumberInput(
                        attrs={
                            "class": "form-control",
                            "step": "any",
                        }
                    ),
                )

            elif pregunta.tipo_respuesta == pregunta.TipoRespuesta.FECHA:
                campo = forms.DateField(
                    **argumentos,
                    widget=forms.DateInput(
                        attrs={
                            "class": "form-control",
                            "type": "date",
                        }
                    ),
                )

            else:
                campo = forms.CharField(
                    **argumentos,
                    widget=forms.TextInput(
                        attrs={
                            "class": "form-control",
                        }
                    ),
                )

            self.fields[nombre_campo] = campo

