from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Animal
from .views import notificar_nuevo_animal
import django.apps


def get_PerfilUsuario():
    return django.apps.apps.get_model('adopciones', 'PerfilUsuario')

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario = get_PerfilUsuario()
        PerfilUsuario.objects.create(usuario=instance)


@receiver(post_save, sender=Animal)
def enviar_notificacion_nuevo_animal(sender, instance, created, **kwargs):
    if created:
        print(f"🐾 Nuevo animal creado: {instance.nombre}")
        notificar_nuevo_animal(instance.nombre)

