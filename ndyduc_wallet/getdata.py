import os
import django
import json
from ndyduc_wallet import views

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ndyducAPI.settings')

django.setup()


from ndyduc_wallet.models import User

def main():
    views.view_all_users()






