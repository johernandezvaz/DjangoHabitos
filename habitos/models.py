from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Habito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.ForeignKey('Icono', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class RegistroDiario(models.Model):
    habito = models.ForeignKey(Habito, on_delete=models.CASCADE)
    fecha = models.DateField()
    cumplido = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habito', 'fecha')

class Icono(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='iconos/')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nombre', 'usuario')  # <- esto evita duplicados por usuario

    def __str__(self):
        return self.nombre

class Recordatorio(models.Model):
    habito = models.ForeignKey(Habito, on_delete=models.CASCADE, related_name='recordatorios')
    mensaje = models.CharField(max_length=255)
    hora = models.TimeField()
    frecuencia = models.CharField(
        max_length=20,
        choices=[('diario', 'Diario'), ('semanal', 'Semanal')],
        default='diario'
    )

    def __str__(self):
        return f"{self.habito.nombre} - {self.hora.strftime('%H:%M')} ({self.frecuencia})"

class Progreso(models.Model):
    habito = models.ForeignKey('Habito', on_delete=models.CASCADE)
    fecha = models.DateField()
    completado = models.BooleanField(default=False)

    def clean(self):
        hoy = timezone.localdate()
        if self.fecha != hoy:
            raise ValidationError("Solo puedes registrar el progreso para la fecha de hoy.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Esto garantiza que se llame a `clean()` antes de guardar
        super().save(*args, **kwargs)