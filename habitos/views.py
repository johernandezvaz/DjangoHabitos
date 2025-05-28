from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import HabitoForm, RegistroUsuarioForm, IconoForm, RecordatorioForm, PerfilForm
from .models import Habito, RegistroDiario, Recordatorio
from datetime import date
from calendar import Calendar
import calendar


# Views de Habito
@never_cache
@login_required
def crear_habito(request):
    if request.method == 'POST':
        form = HabitoForm(request.POST, usuario=request.user)
        if form.is_valid():
            habito = form.save(commit=False)
            habito.usuario = request.user
            habito.save()
            return redirect('lista_habitos')
    else:
        form = HabitoForm(usuario=request.user)
    return render(request, 'habitos/crear_habito.html', {'form': form})


@never_cache
@login_required
def lista_habitos(request):
    habitos = Habito.objects.filter(usuario=request.user).select_related('icono').prefetch_related('recordatorios').order_by('-fecha_creacion')
    return render(request, 'habitos/lista_habitos.html', {'habitos': habitos})

@never_cache
@login_required
def detalle_habito(request, habito_id):
    habito = get_object_or_404(Habito, id=habito_id, usuario=request.user)

    hoy = date.today()
    cal = Calendar(firstweekday=0)
    semanas = list(cal.monthdatescalendar(hoy.year, hoy.month))

    # Días que se marcaron como cumplidos
    registros = RegistroDiario.objects.filter(
        habito=habito,
        fecha__year=hoy.year,
        fecha__month=hoy.month,
        cumplido=True
    ).values_list('fecha', flat=True)

    cumplidos = set(registros)

    # Días hasta hoy 
    dias_no_cumplidos = set()
    for semana in semanas:
        for dia in semana:
            if dia.month == hoy.month and dia <= hoy and dia >= habito.fecha_creacion.date():
                if dia not in cumplidos:
                    dias_no_cumplidos.add(dia)

    context = {
        'habito': habito,
        'semanas': semanas,
        'cumplidos': cumplidos,
        'no_cumplidos': dias_no_cumplidos,
        'hoy': hoy,
    }
    return render(request, 'habitos/detalle_habito.html', context)


@never_cache
@login_required
def editar_habito(request, habito_id):
    habito = get_object_or_404(Habito, id=habito_id, usuario=request.user)
    
    if request.method == 'POST':
        form = HabitoForm(request.POST, instance=habito, usuario=request.user) 
        if form.is_valid():
            form.save()
            return redirect('lista_habitos')
    else:
        form = HabitoForm(instance=habito, usuario=request.user)

    return render(request, 'habitos/editar_habito.html', {'form': form, 'habito': habito})


@never_cache
@login_required
def eliminar_habito(request, habito_id):
    habito = get_object_or_404(Habito, id=habito_id, usuario=request.user)

    if request.method == 'POST':
        habito.delete()
        return redirect('lista_habitos') 

    return render(request, 'habitos/eliminar_habito.html', {'habito': habito})

@never_cache
@login_required
def marcar_dia(request, habito_id, year, month, day):
    habito = get_object_or_404(Habito, id=habito_id, usuario=request.user)
    
    fecha = date(year=int(year), month=int(month), day=int(day))
    
    registro, creado = RegistroDiario.objects.get_or_create(habito=habito, fecha=fecha)
    
    registro.cumplido = not registro.cumplido
    registro.save()
    
    return redirect('detalle_habito', habito_id=habito.id)

@never_cache
@login_required
def crear_icono(request):
    if request.method == 'POST':
        form = IconoForm(request.POST, request.FILES)  
        if form.is_valid():
            icono = form.save(commit=False)
            icono.usuario = request.user
            icono.save()
            return redirect('lista_habitos')  
    else:
        form = IconoForm()
    return render(request, 'habitos/crear_icono.html', {'form': form})

@never_cache
@login_required
def formulario_view(request):
    if request.method == 'POST':
        form = HabitoForm(request.POST)
        if form.is_valid():
            habito = form.save(commit=False)
            habito.usuario = request.user  
            habito.save()
            return redirect('index') 
    else:
        form = HabitoForm()
    
    return render(request, 'habitos/formulario.html', {'form': form})

# Views de recordatorio
@never_cache
@login_required
def crear_recordatorio(request, habito_id):
    habito = get_object_or_404(Habito, pk=habito_id, usuario=request.user)  
    
    if request.method == 'POST':
        form = RecordatorioForm(request.POST, user=request.user)  
        if form.is_valid():
            recordatorio = form.save(commit=False)
            recordatorio.habito = habito
            recordatorio.save()
            return redirect('ver_recordatorio', habito_id=habito.id)
    else:
        form = RecordatorioForm(user=request.user) 
    
    return render(request, 'habitos/crear_recordatorio.html', {'form': form, 'habito': habito})


@never_cache
@login_required
def ver_recordatorio(request, habito_id):
    habito = get_object_or_404(Habito, pk=habito_id)
    recordatorios = habito.recordatorios.all()

    return render(request, 'habitos/ver_recordatorio.html', {
        'habito': habito,
        'recordatorios': recordatorios,
    })

@never_cache
@login_required
def enviar_recordatorio(request, habito_id):
    habito = get_object_or_404(Habito, pk=habito_id)

    # Envía correo solo cuando se accede a esta vista
    send_mail(
        subject=f'Recordatorio: {habito.nombre}',
        message=f'¡Hola! Este es tu recordatorio para el hábito: "{habito.nombre}".',
        from_email='felixmancinas7@gmail.com',
        recipient_list=[request.user.email],
        fail_silently=False,
    )

    messages.success(request, 'Recordatorio enviado correctamente.')
    return HttpResponseRedirect(reverse('ver_recordatorio', args=[habito_id]))

def enviar_correo(recordatorio):
    usuario = recordatorio.habito.usuario
    send_mail(
        subject=f"Recordatorio de tu hábito: {recordatorio.habito.nombre}",
        message=recordatorio.mensaje,
        from_email='afjdjangotest.com',
        recipient_list=[usuario.email],
        fail_silently=True,
    )


@never_cache
@login_required
def editar_recordatorio(request, recordatorio_id):
    recordatorio = get_object_or_404(Recordatorio, pk=recordatorio_id)
    habito = recordatorio.habito
    if request.method == 'POST':
        form = RecordatorioForm(request.POST, instance=recordatorio)
        if form.is_valid():
            form.save()
            return redirect('ver_recordatorio', habito_id=habito.id)
    else:
        form = RecordatorioForm(instance=recordatorio)
    return render(request, 'habitos/editar_recordatorio.html', {'form': form, 'habito': habito})


@never_cache
@login_required
def eliminar_recordatorio(request, recordatorio_id):
    recordatorio = get_object_or_404(Recordatorio, pk=recordatorio_id)
    habito = recordatorio.habito
    if request.method == 'POST':
        recordatorio.delete()
        return redirect('ver_recordatorio', habito_id=habito.id)
    return render(request, 'habitos/eliminar_recordatorio.html', {'recordatorio': recordatorio, 'habito': habito})

def index(request):
    if request.user.is_authenticated:
        return redirect('lista_habitos')
    else:
        return redirect('login')  

@never_cache
def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login") 
    else:
        form = RegistroUsuarioForm()
    return render(request, "registration/registro_usuario.html", {"form": form})

def cerrar_sesion(request):
    logout(request)
    return redirect('login')

@never_cache
@login_required
def editar_perfil(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        user = request.user
        user.username = username
        user.email = email
        user.save()

        messages.success(request, 'Tu perfil ha sido actualizado con éxito.')  
        return redirect('editar_perfil')  

    return render(request, 'registration/editar_perfil.html')

@never_cache
@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # para mantener sesión activa
            messages.success(request, 'Contraseña cambiada correctamente.')
            return redirect('cambiar_contrasena')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'habitos/cambiar_contrasena.html', {'form': form})

