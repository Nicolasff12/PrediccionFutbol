from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Usuario


class RegistroForm(UserCreationForm):
    """Formulario de registro de usuarios"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('telefono', css_class='form-group col-md-6 mb-3'),
                Column('fecha_nacimiento', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', 'Registrarse', css_class='btn btn-primary w-100')
        )
        for field_name, field in self.fields.items():
            if field_name not in ['username', 'email', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento']:
                field.widget.attrs.update({'class': 'form-control'})


class PerfilForm(UserChangeForm):
    """Formulario de edición de perfil"""
    password = None  # No mostrar campo de contraseña en el formulario

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento', 'foto_perfil')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('telefono', css_class='form-group col-md-6 mb-3'),
                Column('fecha_nacimiento', css_class='form-group col-md-6 mb-3'),
            ),
            'foto_perfil',
            Submit('submit', 'Guardar Cambios', css_class='btn btn-primary')
        )
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class LoginForm(forms.Form):
    """Formulario de login"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Iniciar Sesión', css_class='btn btn-primary w-100 mt-3')
        )

