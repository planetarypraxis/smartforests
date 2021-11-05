worker() {
  sleep 720
  python manage.py runcrons
}

worker & gunicorn --worker-tmp-dir /dev/shm smartforests.wsgi
