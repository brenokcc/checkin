import re
import base64
from uuid import uuid1
import tempfile
import datetime
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Checkin, Pessoa, PontoCheckin

try:
    import face_recognition
except ImportError:
    pass

def get_device_id(request):
    user_agent = request.headers['User-Agent']
    x = re.sub(r'\d|\(|\)', '.', user_agent)
    return base64.b64encode(x.encode()).decode()


def check_device_id(device_id, request):
    user_agent = request.headers['User-Agent']
    x = base64.b64decode(device_id.encode()).decode()
    return bool(re.search(x, user_agent))


def checkins(request, token):
    pessoa = Pessoa.objects.get(token=token)
    return render(request, 'checkins.html', dict(pessoa=pessoa))


@csrf_exempt
def checkin(request, token, token_pessoa=None):
    autorizado = True
    if token_pessoa is None:
        ponto_checkin = None
        pessoa = Pessoa.objects.get(token=token)
        redirect_url = '/checkins/{}/'.format(pessoa.token)
        if pessoa.dispositivo is None:
            pessoa.dispositivo = get_device_id(request)
            pessoa.save()
        autorizado = check_device_id(pessoa.dispositivo, request)
    else:
        ponto_checkin = PontoCheckin.objects.get(token=token)
        redirect_url = '/start/{}/'.format(ponto_checkin.token)
        pessoa = Pessoa.objects.get(aplicacao=ponto_checkin.aplicacao, token=token_pessoa)
    if request.POST:
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
        ponto_mais_proximo = pessoa.aplicacao.localizar_ponto_mais_proximo(latitude, longitude)
        if ponto_mais_proximo:
            file_path = tempfile.mktemp(suffix='.jpeg')
            file = open(file_path, 'wb')
            file.write(base64.b64decode(request.POST['image'][23:]))
            file.close()
            # print(file_path)
            # print(pessoa.foto.path)
            # checkin = Checkin.objects.create(
            #     uuid=uuid1().hex, pessoa=pessoa, latitude=latitude, ponto=ponto_checkin,
            #     longitude=longitude, data_hora=datetime.datetime.now()
            # )
            # return HttpResponse(json.dumps(dict(uuid=checkin.uuid)))

            if1 = face_recognition.load_image_file(file_path)
            if2 = face_recognition.load_image_file(pessoa.foto.path)
            fe1 = face_recognition.face_encodings(if1)
            fe2 = face_recognition.face_encodings(if2)
            if fe1 and fe2:
                result = face_recognition.compare_faces([fe1[0]], fe2[0])
                if result[0]:
                    checkin = Checkin.objects.create(
                        uuid=uuid1().hex, pessoa=pessoa, latitude=latitude, ponto=ponto_checkin,
                        longitude=longitude, data_hora=datetime.datetime.now()
                    )
                    return HttpResponse(json.dumps(dict(uuid=checkin.uuid)))
            return HttpResponse(json.dumps(dict(message='Pessoa não identificada!')))
        return HttpResponse(json.dumps(dict(message='Localização inválida!')))
    return render(request, 'checkin.html', dict(pessoa=pessoa, autorizado=autorizado, redirect_url=redirect_url))


def start(request, token):
    ponto_checkin = PontoCheckin.objects.get(token=token)
    print(request.headers['User-Agent'])
    return render(request, 'start.html', dict(ponto_checkin=ponto_checkin))


def end(request, uuid):
    checkin = Checkin.objects.get(uuid=uuid)
    if 'ponto' in request.GET and request.GET['ponto']:
        redirect_url = '/start/'
    return render(request, 'end.html', dict(checkin=checkin))


def photos(request):
    return render(request, 'photos.html', dict())
