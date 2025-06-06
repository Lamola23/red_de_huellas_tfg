from django.db import models
from django.contrib.auth.models import User

# --- Roles específicos ---
class Administrador(models.Model):
    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Veterinario(models.Model):
    nombre = models.CharField(max_length=100)
    numero_colegiado = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Centro(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    ciudad = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100, default='No especificado')
    edad = models.IntegerField(default=18)
    telefono = models.CharField(max_length=20, default='000000000')
    codigo_postal = models.CharField(max_length=10, default='00000')

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"


# --- PerfilUsuario con relación a uno de los roles ---
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    quiere_notificaciones = models.BooleanField(default=False)
    usuario_simple = models.OneToOneField('Usuario', on_delete=models.SET_NULL, null=True, blank=True)

    administrador = models.OneToOneField(Administrador, on_delete=models.SET_NULL, null=True, blank=True)
    veterinario = models.OneToOneField(Veterinario, on_delete=models.SET_NULL, null=True, blank=True)
    centro = models.OneToOneField(Centro, on_delete=models.SET_NULL, null=True, blank=True)

    def obtener_rol(self):
        if self.administrador:
            return "admin"
        elif self.veterinario:
            return "veterinario"
        elif self.centro:
            return "centro"
        elif self.usuario_simple:
            return "usuario"
        else:
            return "desconocido"


    def __str__(self):
        try:
            if self.usuario_simple:
                return f"{self.usuario_simple.nombre} (Usuario)"
            elif self.veterinario:
                return f"{self.veterinario.nombre} (Veterinario)"
            elif self.centro:
                return f"{self.centro.nombre} (Centro)"
            elif self.administrador:
                return f"{self.administrador.nombre} (Admin)"
            else:
                return f"{self.usuario.username} (desconocido)"
        except:
            return "Perfil sin usuario"


# --- Animal y relaciones ---
class Animal(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=50, blank=True)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=10)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True)
    fecha_ingreso = models.DateField(verbose_name="Fecha de ingreso")
    adoptado = models.BooleanField(default=False)
    adoptante = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    foto = models.ImageField(upload_to='animales/', null=True, blank=True, verbose_name="Foto del animal")
    en_tratamiento = models.BooleanField(default=False)
    pendiente_vacuna = models.BooleanField(default=False)
    urgente = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animales"

    def __str__(self):
        return self.nombre

# --- Historial veterinario ---
class Historial(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    evento = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Historial"
        verbose_name_plural = "Historiales"

    def __str__(self):
        return f"{self.animal.nombre} - {self.evento}"


########################################################################################################

from django.db import models
from .models import Animal, Veterinario

class Cita(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    motivo = models.TextField()

    def __str__(self):
        return f"Cita de {self.animal.nombre} con {self.veterinario.nombre} el {self.fecha.strftime('%d/%m/%Y %H:%M')}"


##################################################################################################################

class Informe(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    
    def __str__(self):
        return f"Informe de {self.animal.nombre} - {self.fecha.strftime('%Y-%m-%d')}"

################################################################################################################

class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Veterinario, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

##################################################################################################################