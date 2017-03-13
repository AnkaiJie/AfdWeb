from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from afd.tasks import send_result


def index(request):
    template = loader.get_template('afd/index.html')
    return HttpResponse(template.render(request))

@csrf_exempt
def authorRequest(request):
    auth_id = request.POST.get("author_id", "")
    template = loader.get_template('afd/finish.html')
    send_result.delay(auth_id)
    return HttpResponse(template.render(request))

