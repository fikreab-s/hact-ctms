@echo off
docker exec hact-django-api python manage.py makemigrations clinical --name=edc_skip_logic_audit_trail_visit_form
docker exec hact-django-api python manage.py migrate clinical
echo DONE
