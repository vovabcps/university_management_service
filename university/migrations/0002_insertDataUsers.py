from django.db import migrations, transaction
from ..models import *
from django.contrib.auth.models import User



@transaction.atomic
def makeAuth_userOBJs(apps, schema_editor):
    #800 users
    #3 admins
    newUSER= User.objects.create_user(username="adminF1", password="damabranca1", is_superuser=True, is_staff=True)
    newUSER= User.objects.create_user(username="adminF2", password="damabranca2", is_superuser=True, is_staff=True)
    newUSER= User.objects.create_user(username="adminF3", password="damabranca3", is_superuser=True, is_staff=True)
    newUSER.save()
    for _ in range(797): #797 rest
        obj = User.objects.latest('id')
        newUSER= User.objects.create_user(username="fc"+str((obj.id+1)), password="blabla"+str((obj.id+1)), is_superuser=False)
        newUSER.save()



class Migration(migrations.Migration):
    dependencies = [
        ('university', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(makeAuth_userOBJs)
    ]








