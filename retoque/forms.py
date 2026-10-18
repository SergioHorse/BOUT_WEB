from django import forms
from .models import Retoque


class RetoqueForm(forms.ModelForm):

    class Meta:
        model = Retoque
        fields = '__all__'
