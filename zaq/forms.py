from django import forms
from .models import Engine, Detail

class EngineForm(forms.ModelForm):

    details = forms.ModelMultipleChoiceField(queryset=Detail.objects.none(),
                                             widget=forms.CheckboxSelectMultiple(),
                                             required=True,
                                             label='Seleccionar fallos o retoques')

    class Meta:
        model = Engine
        fields = ['code_bar', 'details']

        widgets = {
            'code_bar': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Escanea código de barras',
                                               'autocomplete': 'off',
                                               }
                                        ),
        }

    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        if category is not None:
            self.fields['details'].queryset = Detail.objects.filter(
                category=category,active=True).order_by('order', 'name')



