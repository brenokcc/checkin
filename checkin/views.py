import re
import base64
from uuid import uuid1
import tempfile
import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Checkin, Pessoa

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


@csrf_exempt
def checkin(request, token, chave_pessoa=None):
    if chave_pessoa is None:
        pessoa = Pessoa.objects.get(token=token)
        if pessoa.dispositivo is None:
            pessoa.dispositivo = get_device_id(request)
            pessoa.save()
        autorizado = check_device_id(pessoa.dispositivo, request)
    else:
        autorizado = True
        pessoa = Pessoa.objects.get(aplicacao__token=token, chave=chave_pessoa)
    if request.POST:
        file_path = tempfile.mktemp(suffix='.jpeg')
        file = open(file_path, 'wb')
        file.write(base64.b64decode(request.POST['image'][23:]))
        file.close()
        print(file_path)
        print(pessoa.foto.path)
        if1 = face_recognition.load_image_file(file_path)
        if2 = face_recognition.load_image_file(pessoa.foto.path)
        fe1 = face_recognition.face_encodings(if1)
        fe2 = face_recognition.face_encodings(if2)
        if fe1 and fe2:
            result = face_recognition.compare_faces([fe1[0]], fe2[0])
            if result[0]:
                checkin = Checkin.objects.create(
                    uuid=uuid1().hex, pessoa=pessoa, latitude=request.POST['latitude'],
                    longitude=request.POST['longitude'], data_hora=datetime.datetime.now()
                )
                return HttpResponse('/end/{}/'.format(checkin.uuid))
        return HttpResponse('')
    return render(request, 'checkin.html', dict(pessoa=pessoa, autorizado=autorizado))


def start(request):
    print(request.headers['User-Agent'])
    return render(request, 'start.html')


def end(request, uuid):
    checkin = Checkin.objects.get(uuid=uuid)
    return render(request, 'end.html', dict(checkin=checkin))
