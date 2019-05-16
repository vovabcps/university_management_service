#para nao ter que passar o mesmo valor para todas a views que extendem um django layouts (like 'base.html')
from .models import *


def request_userData(request):
    u = request.user
    if u.is_authenticated:
      su = SystemUser.objects.get(user=u)
      personalData= PersonalInfo.objects.get(user=su)
      return {'personalData': personalData}
    return {}
