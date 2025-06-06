from django.urls import path
from . import views
from .views import LoginUsuario
from django.contrib.auth.views import LogoutView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.vista_inicio, name='inicio'),
    path('animales/', views.lista_animales, name='lista_animales'),
    path('animal/<int:animal_id>/', views.detalle_animal, name='detalle_animal'),
    path('login/', LoginUsuario.as_view(), name='login'),
    path('registro/', views.registro_usuario, name='registro'),
    path('registro/centro/', views.registro_centro, name='registro_centro'),
    path('logout/', LogoutView.as_view(next_page='lista_animales'), name='logout'),
    path('inicio_admin/', views.inicio_admin, name='inicio_admin'),
    path('inicio_veterinario/', views.inicio_veterinario, name='inicio_veterinario'),
    path('inicio_centro/', views.inicio_centro, name='inicio_centro'),
    path('inicio_usuario/', views.inicio_usuario, name='inicio_usuario'),
    path('veterinario/historial/<int:animal_id>/', views.añadir_historial, name='añadir_historial'),
    path('veterinario/historial/completo/<int:animal_id>/', views.ver_historial_animal, name='ver_historial_animal'),
    path('veterinario/inicio/', views.inicio_veterinario, name='inicio_veterinario'),
    path('animales/nuevo/', views.crear_animal, name='crear_animal'),
    path('veterinario/nueva-cita/', views.crear_cita, name='crear_cita'),
    path('veterinario/citas/', views.listar_citas, name='listar_citas'),
    path('veterinario/informe/nuevo/', views.crear_informe, name='crear_informe'),
    path('veterinario/informes/', views.listar_informes, name='listar_informes'),
    path('veterinario/medicamentos/nuevo/', views.crear_medicamento, name='crear_medicamento'),
    path('veterinario/medicamentos/', views.listar_medicamentos, name='listar_medicamentos'),
    path('veterinario/animal/<int:animal_id>/estado/', views.editar_estado_animal, name='editar_estado_animal'),
    path('veterinario/animales/', views.lista_animales_veterinario, name='lista_animales_veterinario'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('silk/', include('silk.urls', namespace='silk')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
