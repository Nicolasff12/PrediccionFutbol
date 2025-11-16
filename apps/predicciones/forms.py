from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit


class PrediccionForm(forms.Form):
    """Formulario para crear predicción manual"""
    goles_local = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Goles local'})
    )
    goles_visitante = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Goles visitante'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('goles_local', css_class='form-group col-md-6 mb-3'),
                Column('goles_visitante', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', 'Guardar Predicción', css_class='btn btn-primary w-100')
        )

