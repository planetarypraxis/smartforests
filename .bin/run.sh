python manage.py process_tasks & gunicorn --workers=2 --threads=2 --worker-tmp-dir /dev/shm smartforests.wsgi
