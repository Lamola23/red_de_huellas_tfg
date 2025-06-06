

from django.contrib import admin
from .models import (
    Centro, Animal, Usuario, Historial,
    Administrador, Veterinario, PerfilUsuario
)

from django.contrib.auth.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff']

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(Centro)
admin.site.register(Animal)
admin.site.register(Usuario)
admin.site.register(Historial)
admin.site.register(Administrador)
admin.site.register(Veterinario)
admin.site.register(PerfilUsuario)

##########################################################################


class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'edad', 'en_tratamiento', 'pendiente_vacuna', 'urgente')
    list_filter = ('en_tratamiento', 'pendiente_vacuna', 'urgente')

