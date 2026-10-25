from django import forms
from .models import Rodaje
from zaq.models import Engine


class RodajeForm(forms.ModelForm):
    code_bar = forms.CharField(
        label='Código de barras',
        max_length=100,
        widget=forms.TextInput(attrs={'id': 'id_codigo_barras',
                                      'class': 'form-control',
                                      'placeholder': 'Introduce el código de barras',
                                      'autofocus': True})
    )

    class Meta:
        model = Rodaje

        fields = [
            'code_bar',
            'resultado',
            'observations',

        ]

        widgets = {
            'resultado': forms.Select(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control',
                                                  'rows': 4}),
        }

    def clean_code_bar(self):
        codigo = self.cleaned_data['code_bar'].strip()

        try:
            engine = Engine.objects.get(code_bar=codigo)
        except Engine.DoesNotExist:
            raise forms.ValidationError(
                'No existe ningún motor con ese código de barras.'
            )
        except Engine.MultipleObjectsReturned:
            raise forms.ValidationError(
                'Hay varios motores con ese código de barras.'
            )

        return engine

    def save(self, commit=True):
        rodaje = super().save(commit=False)

        rodaje.engine = self.cleaned_data['code_bar']

        if commit:
            rodaje.save()
            self.save_m2m()

        return rodaje
