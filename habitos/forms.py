from django import forms
from .models import Habito, Icono, Recordatorio
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User

class RegistroUsuarioForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        help_text="Solo letras, números y @/./+/-/_"
    )
    email = forms.EmailField(required=True, label="Correo electrónico")
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        help_text="Debe tener al menos 8 caracteres y no ser muy común."
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        help_text="Debe coincidir con la contraseña anterior."
    )


    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class HabitoForm(forms.ModelForm):
    class Meta:
        model = Habito
        fields = ['nombre', 'descripcion', 'icono']

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['icono'].queryset = Icono.objects.filter(usuario=usuario)

class PerfilForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(required=True, label="Nombre")

    class Meta:
        model = User
        fields = ['first_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tucorreo@ejemplo.com'}),
        }


class IconoForm(forms.ModelForm):
    class Meta:
        model = Icono
        fields = ['nombre', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del icono'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class RecordatorioForm(forms.ModelForm):
    class Meta:
        model = Recordatorio
        fields = ['habito', 'mensaje', 'hora', 'frecuencia']
        widgets = {
            'habito': forms.Select(attrs={'class': 'form-control'}),
            'mensaje': forms.TextInput(attrs={'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Sacamos user de kwargs
        super().__init__(*args, **kwargs)
        if user is not None:
            # Filtramos hábitos para que solo se muestren los que pertenecen a ese usuario
            self.fields['habito'].queryset = Habito.objects.filter(usuario=user)
