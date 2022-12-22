python manage.py process_tasks & gunicorn --workers=2 --worker-tmp-dir /dev/shm smartforests.asgi -k uvicorn.workers.UvicornWorker
