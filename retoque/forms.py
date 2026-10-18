
from django import forms
from .models import Retoque


class RetoqueForm(forms.ModelForm):
    class Meta:
        model = Retoque
        fields = [
            'engine',
            'status',
            'operator',
            'observations',
            'date_analysis',
            'allocation_retouching_cost',
        ]
        widgets = {
            'date_analysis': forms.DateInput(attrs={'type': 'date'}),
            'observations': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if isinstance(field.widget, forms.CheckboxInput):
                css += ' form-check-input'
            else:
                css += ' form-control'
            field.widget.attrs['class'] = css.strip()
