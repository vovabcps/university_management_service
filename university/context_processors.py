#para nao ter que passar o mesmo valor para todas a views que extendem um django layouts (like 'base.html')
from .models import *


def request_userData(request):
    u = request.user
    if u.is_authenticated:
      su = SystemUser.objects.get(user=u)
      personalData= PersonalInfo.objects.get(user=su)
      pedidos = list(SystemUserMensagens.objects.filter(destinatario=su))

      listPedidos = []
      for p in pedidos:
        remetente = PersonalInfo.objects.get(user=p.remetente)
        subj = p.subject
        status = p.is_accepted
        if status != True and status != False:
          listPedidos.append((remetente, subj))

      return {'personalData': personalData, 'pedidosNotification': listPedidos}
    return {}

