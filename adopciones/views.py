from django.shortcuts import render
from .models import Animal
from .forms import (
    RegistroInteresadoForm, AnimalForm, CitaForm, 
    InformeForm, MedicamentoForm, EstadoAnimalForm,
    EditarPerfilForm, RegistroCentroForm
)

def lista_animales(request):
    filtro = request.GET.get('filtro')
    
    # Comenzar con todos los animales no adoptados
    animales = Animal.objects.filter(adoptado=False)
    
    # Aplicar filtros adicionales según el parámetro
    if filtro == 'tratamiento':
        animales = animales.filter(en_tratamiento=True)
    elif filtro == 'vacuna':
        animales = animales.filter(pendiente_vacuna=True)
    elif filtro == 'urgente':
        animales = animales.filter(urgente=True)
    
    # Añadir print para debug
    print(f"Filtro aplicado: {filtro}")
    print(f"Número de animales encontrados: {animales.count()}")
    
    return render(request, 'animales.html', {'animales': animales})

from django.shortcuts import get_object_or_404

def detalle_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    return render(request, 'animal_detalle.html', {'animal': animal})

from django.shortcuts import redirect

def redireccion_inicio(request):
    return redirect('lista_animales')

#################################################################

from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class LoginUsuario(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        perfil = self.request.user.perfilusuario
        rol = perfil.obtener_rol()
        if rol == 'veterinario':
            return reverse_lazy('inicio_veterinario')
        elif rol == 'centro':
            return reverse_lazy('inicio_centro')
        elif rol == 'admin':
            return reverse_lazy('inicio_admin')
        return reverse_lazy('inicio_usuario')




#########################################################################
from django.shortcuts import render, redirect

def vista_inicio(request):
    if request.user.is_authenticated:
        perfil = request.user.perfilusuario
        rol = perfil.obtener_rol()

        if rol == 'admin':
            return redirect('inicio_admin')
        elif rol == 'veterinario':
            return redirect('inicio_veterinario')
        elif rol == 'centro':
            return redirect('inicio_centro')
        elif rol == 'usuario':
            return redirect('inicio_usuario')
    
    # Para usuarios no autenticados, mostrar la página de inicio pública
    # Obtener algunos animales para mostrar
    animales_destacados = Animal.objects.filter(adoptado=False).order_by('?')[:6]
    animales_urgentes = Animal.objects.filter(urgente=True, adoptado=False)[:3]
    
    return render(request, 'inicio_publico.html', {
        'animales_destacados': animales_destacados,
        'animales_urgentes': animales_urgentes,
    })



from django.http import HttpResponseForbidden

def inicio_admin(request):
    if not request.user.is_authenticated:
        return redirect('login')

    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'admin':
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    return render(request, 'inicio_admin.html')

def inicio_veterinario(request):
    return render(request, 'inicio_veterinario.html')

def inicio_centro(request):
    return render(request, 'inicio_centro.html')

def inicio_usuario(request):
    return render(request, 'inicio_usuario.html')


from django.http import HttpResponseForbidden
from .models import Animal, Historial
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

#####################################################################################################
def inicio_veterinario(request):
    return render(request, 'inicio_veterinario.html')



def añadir_historial(request, animal_id):
    if not request.user.is_authenticated:
        return redirect('login')

    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Solo los veterinarios pueden añadir historiales.")

    animal = get_object_or_404(Animal, id=animal_id)

    if request.method == 'POST':
        evento = request.POST.get('evento')
        if evento:
            Historial.objects.create(animal=animal, evento=evento, fecha=timezone.now())

    return redirect('inicio_veterinario')


def ver_historial_animal(request, animal_id):
    if not request.user.is_authenticated:
        return redirect('login')

    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Solo los veterinarios pueden ver historiales.")

    animal = get_object_or_404(Animal, id=animal_id)
    historial = Historial.objects.filter(animal=animal).order_by('-fecha')

    return render(request, 'historial_animal.html', {
        'animal': animal,
        'historial': historial
    })


##############################################################################################################
from .forms import RegistroInteresadoForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from adopciones.models import PerfilUsuario

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroInteresadoForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)

            perfil = PerfilUsuario.objects.get(usuario=usuario)
            rol = perfil.obtener_rol()

            if rol == 'usuario':
                return redirect('inicio_usuario')
            elif rol == 'admin':
                return redirect('inicio_admin')
            elif rol == 'centro':
                return redirect('inicio_centro')
            elif rol == 'veterinario':
                return redirect('inicio_veterinario')
            else:
                return redirect('inicio')  # Vista pública

    else:
        form = RegistroInteresadoForm()
    return render(request, 'registro.html', {'form': form})



from django.core.mail import send_mail
from adopciones.models import PerfilUsuario

def notificar_nuevo_animal(nombre_animal):
    interesados = PerfilUsuario.objects.filter(quiere_notificaciones=True, usuario_simple__isnull=False)
    emails = [p.usuario.email for p in interesados]

    if emails:
        send_mail(
            subject=f"Nuevo animal disponible: {nombre_animal}",
            message=f"Se ha publicado un nuevo animal en Red de Huellas: {nombre_animal}. ¡Échale un vistazo!",
            from_email=None,  # Usa DEFAULT_FROM_EMAIL
            recipient_list=emails,
            fail_silently=False,
        )


###########################################################################################################################

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Animal, Historial

@login_required
def inicio_veterinario(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Acceso restringido a veterinarios.")

    # Obtener todos los animales no adoptados
    animales = Animal.objects.filter(adoptado=False)
    
    # Contar animales por categoría
    en_tratamiento = animales.filter(en_tratamiento=True).count()
    pendientes_vacuna = animales.filter(pendiente_vacuna=True).count()
    urgentes = animales.filter(urgente=True).count()
    total_animales = animales.count()

    # Obtener las últimas citas
    citas = Cita.objects.filter(veterinario=perfil.veterinario).order_by('fecha')[:5]
    
    # Obtener los últimos informes
    informes = Informe.objects.filter(veterinario=perfil.veterinario).order_by('-fecha')[:5]

    # Filtrar animales según el parámetro
    filtro = request.GET.get('filtro')
    if filtro == 'tratamiento':
        animales = animales.filter(en_tratamiento=True)
    elif filtro == 'vacuna':
        animales = animales.filter(pendiente_vacuna=True)
    elif filtro == 'urgente':
        animales = animales.filter(urgente=True)

    context = {
        "animales": animales,
        "en_tratamiento": en_tratamiento,
        "pendientes_vacuna": pendientes_vacuna,
        "urgentes": urgentes,
        "total_animales": total_animales,
        "citas": citas,
        "informes": informes,
        "filtro_actual": filtro or 'todos'
    }

    return render(request, 'inicio_veterinario.html', context)

################################################################################################################################

from django.shortcuts import render, redirect
from .forms import AnimalForm
from django.contrib.auth.decorators import login_required

@login_required
def crear_animal(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() not in ['veterinario', 'centro']:
        return HttpResponseForbidden("Solo veterinarios y centros pueden añadir animales.")

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False)
            # Si es un centro, asignar automáticamente el centro
            if perfil.obtener_rol() == 'centro':
                animal.centro = perfil.centro
            animal.save()
            messages.success(request, f'El animal {animal.nombre} ha sido registrado correctamente.')
            return redirect('lista_animales')
    else:
        initial_data = {}
        # Si es un centro, pre-seleccionar el centro y ocultarlo
        if perfil.obtener_rol() == 'centro':
            initial_data['centro'] = perfil.centro
        form = AnimalForm(initial=initial_data)
        
        # Si es un centro, eliminar el campo centro del formulario
        if perfil.obtener_rol() == 'centro':
            del form.fields['centro']
    
    return render(request, 'crear_animal.html', {'form': form})


##########################################################Citas############################################################################

from django.shortcuts import render, redirect
from .forms import CitaForm
from django.contrib.auth.decorators import login_required

@login_required
def crear_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio_veterinario')
    else:
        form = CitaForm()

    return render(request, 'crear_cita.html', {'form': form})


from .models import Cita
from django.contrib.auth.decorators import login_required

@login_required
def listar_citas(request):
    perfil = request.user.perfilusuario

    # Si el usuario es veterinario, solo ve sus propias citas
    if perfil.obtener_rol() == 'veterinario':
        citas = Cita.objects.filter(veterinario=perfil.veterinario).order_by('fecha')
    else:
        citas = Cita.objects.all().order_by('fecha')  # admin u otros roles

    return render(request, 'listar_citas.html', {'citas': citas})

#################################################Informes############################################################################

from .forms import InformeForm

@login_required
def crear_informe(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Solo los veterinarios pueden crear informes.")

    if request.method == 'POST':
        form = InformeForm(request.POST)
        if form.is_valid():
            informe = form.save(commit=False)
            informe.veterinario = perfil.veterinario
            informe.save()
            return redirect('inicio_veterinario')  # o a 'listar_informes'
    else:
        form = InformeForm()

    return render(request, 'crear_informe.html', {'form': form})


from .models import Informe  # Asegúrate de tener este modelo creado

@login_required
def listar_informes(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Solo los veterinarios pueden ver los informes.")

    informes = Informe.objects.filter(veterinario=perfil.veterinario).order_by('-fecha')
    return render(request, 'listar_informes.html', {'informes': informes})

###########################################Medicamentos####################################################################################

from .forms import MedicamentoForm
from .models import Medicamento

@login_required
def listar_medicamentos(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Solo los veterinarios pueden ver los medicamentos.")
    
    medicamentos = Medicamento.objects.all().order_by('nombre')
    return render(request, 'listar_medicamentos.html', {'medicamentos': medicamentos})



@login_required
def crear_medicamento(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Solo los veterinarios pueden añadir medicamentos.")

    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            medicamento = form.save(commit=False)
            medicamento.creado_por = perfil.veterinario
            medicamento.save()
            return redirect('listar_medicamentos')
    else:
        form = MedicamentoForm()

    return render(request, 'crear_medicamento.html', {'form': form})


###############################################################################################################################

from .forms import EstadoAnimalForm

@login_required
def editar_estado_animal(request, animal_id):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Solo los veterinarios pueden editar estados.")

    animal = get_object_or_404(Animal, pk=animal_id)

    if request.method == 'POST':
        form = EstadoAnimalForm(request.POST, instance=animal)
        if form.is_valid():
            form.save()
            messages.success(request, f'Estado de {animal.nombre} actualizado correctamente.')
            return redirect('inicio_veterinario')
    else:
        form = EstadoAnimalForm(instance=animal)

    return render(request, 'editar_estado_animal.html', {
        'form': form,
        'animal': animal
    })

###############################################################################################################################

@login_required
def lista_animales_veterinario(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'veterinario':
        return HttpResponseForbidden("Solo los veterinarios pueden ver esta página.")

    filtro = request.GET.get('filtro')

    animales = Animal.objects.all()

    if filtro == 'en_tratamiento':
        animales = animales.filter(en_tratamiento=True)
    elif filtro == 'pendiente_vacuna':
        animales = animales.filter(pendiente_vacuna=True)
    elif filtro == 'urgente':
        animales = animales.filter(urgente=True)

    return render(request, 'lista_animales.html', {'animales': animales})


###############################################################################################################################

@login_required
def editar_perfil(request):
    perfil = request.user.perfilusuario
    
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            return redirect('inicio_usuario')
    else:
        form = EditarPerfilForm(instance=perfil)
    
    return render(request, 'editar_perfil.html', {'form': form})
    
###############################################################################################################################

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def inicio_centro(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != 'centro':
        return HttpResponseForbidden("Acceso denegado.")
    
    return render(request, 'inicio_centro.html')

###############################################################################################################################

def inicio_centro(request):
    perfil = request.user.perfilusuario
    animales = Animal.objects.filter(centro=perfil.centro)

    filtro = request.GET.get('filtro')
    if filtro == 'urgentes':
        animales = animales.filter(urgente=True)
    elif filtro == 'tratamiento':
        animales = animales.filter(en_tratamiento=True)
    elif filtro == 'vacunas':
        animales = animales.filter(pendiente_vacuna=True)
    elif filtro == 'adoptados':
        animales = animales.filter(adoptado=True)
    elif filtro == 'disponibles':
        animales = animales.filter(adoptado=False)

    return render(request, 'inicio_centro.html', {'animales': animales})

###############################################################################################################################

def registro_centro(request):
    if request.method == 'POST':
        form = RegistroCentroForm(request.POST)
        if form.is_valid():
            try:
                centro = form.save()
                messages.success(request, 'Centro registrado correctamente. Por favor, inicia sesión.')
                return redirect('login')
            except IntegrityError:
                messages.error(request, 'Ya existe un centro con ese correo electrónico.')
    else:
        form = RegistroCentroForm()
    
    return render(request, 'registro_centro.html', {'form': form})

###############################################################################################################################

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from adopciones.models import PerfilUsuario, Centro, Veterinario, Animal

@login_required
def inicio_admin(request):
    perfil = request.user.perfilusuario
    if perfil.obtener_rol() != "admin":
        return HttpResponseForbidden("Solo los administradores pueden acceder.")

    total_usuarios = PerfilUsuario.objects.filter(usuario_simple__isnull=False).count()
    total_centros = PerfilUsuario.objects.filter(centro__isnull=False).count()
    total_veterinarios = PerfilUsuario.objects.filter(veterinario__isnull=False).count()
    total_adopciones = Animal.objects.filter(adoptado=True).count()

    context = {
        "total_usuarios": total_usuarios,
        "total_centros": total_centros,
        "total_veterinarios": total_veterinarios,
        "total_adopciones": total_adopciones,
    }

    return render(request, "inicio_admin.html", context)



###############################################################################################################################

from django.db.models.functions import TruncMonth
from django.db.models import Count
from adopciones.models import Animal, PerfilUsuario

# Agrupar adopciones por mes
adopciones_por_mes = (
    Animal.objects.filter(adoptado=True)
    .annotate(mes=TruncMonth("fecha_ingreso"))
    .values("mes")
    .annotate(total=Count("id"))
    .order_by("mes")
)

meses = [a["mes"].strftime("%b %Y") for a in adopciones_por_mes]
totales = [a["total"] for a in adopciones_por_mes]

# Usuarios activos por tipo
activos = PerfilUsuario.objects.values("usuario_simple", "veterinario", "centro")
usuarios_totales = activos.count()
veterinarios = activos.filter(veterinario__isnull=False).count()
centros = activos.filter(centro__isnull=False).count()

context = {
    "meses": meses,
    "totales": totales,
    "usuarios_totales": usuarios_totales,
    "veterinarios": veterinarios,
    "centros": centros,
    # (además del resto de contextos que ya tienes)
}

###############################################################################################################################

