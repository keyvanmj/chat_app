import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Chat_App.settings')
django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import get_default_application

django_asgi_app = get_asgi_application()

application = get_default_application()
