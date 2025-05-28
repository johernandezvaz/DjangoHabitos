web: gunicorn habitos_proyecto.wsgi --log-file - 
#or works good with external database
web: python manage.py migrate && gunicorn habitos_proyecto.wsgi
