from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import subprocess


@api_view(['GET'])
def publish(request):
    if request.method == 'GET':
        if 'Token' in request.headers and request.headers['Token'] == settings.SERVICE_API_TOKEN:
            result = subprocess.run(
                ["python", "manage.py", "publish_scheduled_pages"], stdout=subprocess.PIPE, text=True)
            if (result.returncode == 0):
                print("Finished running 'manage.py publish_scheduled_pages'")
                return Response('OK', status=200)
        return Response('Invalid token', status=403)
