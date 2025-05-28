from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('formulario/', views.formulario_view, name='formulario'),
    path('nuevo/', views.crear_habito, name='crear_habito'),
    path('lista/', views.lista_habitos, name='lista_habitos'),
    path('habito/<int:habito_id>/', views.detalle_habito, name='detalle_habito'),
    path('habitos/eliminar/<int:habito_id>/', views.eliminar_habito, name='eliminar_habito'),
    path('habitos/editar/<int:habito_id>/', views.editar_habito, name='editar_habito'),
    path('icono/crear/', views.crear_icono, name='crear_icono'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('habitos/<int:habito_id>/marcar/<int:year>/<int:month>/<int:day>/', views.marcar_dia, name='marcar_dia'),
    path('habitos/<int:habito_id>/recordatorios/crear/', views.crear_recordatorio, name='crear_recordatorio'),
    path('recordatorios/<int:habito_id>/', views.ver_recordatorio, name='ver_recordatorio'),
    path('habitos/<int:habito_id>/enviar_recordatorio/', views.enviar_recordatorio, name='enviar_recordatorio'),
    path('recordatorios/<int:recordatorio_id>/editar/', views.editar_recordatorio, name='editar_recordatorio'),
    path('recordatorios/<int:recordatorio_id>/eliminar/', views.eliminar_recordatorio, name='eliminar_recordatorio'),
    path('', views.index, name='inicio'),
    path(
        'cambiar-contrasena/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/cambiar_contrasena.html',
            success_url=reverse_lazy('password_change_done')    
        ),
        name='cambiar_contrasena'
    ),
    path(
        'contrasena-cambiada/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/contrasena_cambiada.html'
        ),
        name='password_change_done'
    ),
]
