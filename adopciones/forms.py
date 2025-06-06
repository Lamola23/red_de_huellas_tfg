from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Usuario, PerfilUsuario



class RegistroInteresadoForm(UserCreationForm):
    nombre = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)
    edad = forms.IntegerField(min_value=18, label="Edad")
    telefono = forms.CharField(max_length=20)
    codigo_postal = forms.CharField(max_length=10, label="Código Postal")
    email = forms.EmailField(label="Correo electrónico")
    quiere_notificaciones = forms.BooleanField(
        required=False,
        label="Deseo recibir notificaciones por correo cuando se publiquen nuevos animales"
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            interesado = Usuario.objects.create(
                nombre=self.cleaned_data['nombre'],
                apellidos=self.cleaned_data['apellidos'],
                edad=self.cleaned_data['edad'],
                telefono=self.cleaned_data['telefono'],
                codigo_postal=self.cleaned_data['codigo_postal']
            )

            perfil, creado = PerfilUsuario.objects.get_or_create(usuario=user)
            perfil.usuario_simple = interesado
            perfil.quiere_notificaciones = self.cleaned_data['quiere_notificaciones']
            perfil.save()

        return user
    

from .models import Animal
from django import forms

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'nombre', 'especie', 'raza', 'edad', 'sexo',
            'centro', 'descripcion', 'fecha_ingreso', 'foto'
        ]
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }


#####################################################################################################3333

from django import forms
from .models import Cita

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['animal', 'veterinario', 'fecha', 'motivo']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


#####################################################################################################

from .models import Informe

class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['animal', 'diagnostico', 'tratamiento']
        widgets = {
            'diagnostico': forms.Textarea(attrs={'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'rows': 3}),
        }

############################################################################################################

from django import forms
from .models import Medicamento

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nombre', 'descripcion']

########################################################################################################

from django import forms
from .models import Animal

class EstadoAnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['en_tratamiento', 'pendiente_vacuna', 'urgente']

################################################################################################################

from django import forms
from .models import PerfilUsuario

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['quiere_notificaciones']
        labels = {
            'quiere_notificaciones': 'Recibir notificaciones de nuevos animales'
        }
        widgets = {
            'quiere_notificaciones': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.usuario_simple:
            self.fields['nombre'] = forms.CharField(
                max_length=100,
                initial=self.instance.usuario_simple.nombre,
                required=False
            )
            self.fields['apellidos'] = forms.CharField(
                max_length=100,
                initial=self.instance.usuario_simple.apellidos,
                required=False
            )
            self.fields['telefono'] = forms.CharField(
                max_length=20,
                initial=self.instance.usuario_simple.telefono,
                required=False
            )
            self.fields['codigo_postal'] = forms.CharField(
                max_length=10,
                initial=self.instance.usuario_simple.codigo_postal,
                required=False
            )

    def save(self, commit=True):
        perfil = super().save(commit=False)
        if perfil.usuario_simple:
            if 'nombre' in self.cleaned_data:
                perfil.usuario_simple.nombre = self.cleaned_data['nombre']
            if 'apellidos' in self.cleaned_data:
                perfil.usuario_simple.apellidos = self.cleaned_data['apellidos']
            if 'telefono' in self.cleaned_data:
                perfil.usuario_simple.telefono = self.cleaned_data['telefono']
            if 'codigo_postal' in self.cleaned_data:
                perfil.usuario_simple.codigo_postal = self.cleaned_data['codigo_postal']
            if commit:
                perfil.usuario_simple.save()
        if commit:
            perfil.save()
        return perfil

################################################################################################################

from django import forms
from .models import Centro  # Asegúrate de tener este modelo

class RegistroCentroForm(forms.ModelForm):
    email = forms.EmailField(label="Correo electrónico")
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Centro
        fields = ['nombre', 'direccion', 'telefono', 'ciudad']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        centro = super().save(commit=False)
        centro.correo = self.cleaned_data['email']
        
        if commit:
            # Crear el usuario
            user = User.objects.create_user(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password1']
            )
            
            # Guardar el centro
            centro.save()
            
            # Crear el perfil de usuario y asociarlo con el centro
            perfil = PerfilUsuario.objects.create(
                usuario=user,
                centro=centro
            )
            
        return centro

################################################################################################################