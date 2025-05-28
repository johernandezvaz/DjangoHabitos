from celery import shared_task
from django.core.mail import send_mail
from .models import Recordatorio
from django.utils.timezone import now
from datetime import timedelta

def enviar_correo(recordatorio):
    usuario = recordatorio.habito.usuario
    send_mail(
        subject=f"Recordatorio de tu hábito: {recordatorio.habito.nombre}",
        message=recordatorio.mensaje,
        from_email='afjdjangotest@gmail.com',
        recipient_list=[usuario.email],
        fail_silently=True,
    )

@shared_task
def enviar_recordatorio(*args, **kwargs):
    ahora = now()
    desde = (ahora - timedelta(minutes=1)).time()
    hasta = ahora.time()
    hoy = ahora.date()
    dia_semana_actual = hoy.weekday()

    posibles_recordatorios = Recordatorio.objects.filter(hora__gte=desde, hora__lt=hasta)

    for recordatorio in posibles_recordatorios:
        if recordatorio.frecuencia == 'diario':
            enviar_correo(recordatorio)
        elif recordatorio.frecuencia == 'semanal':
            if recordatorio.habito.fecha_creacion.weekday() == dia_semana_actual:
                enviar_correo(recordatorio)
                print(f"Evaluando recordatorio: {recordatorio}")


