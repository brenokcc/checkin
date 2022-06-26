
import datetime
import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Checkin, Pessoa, PontoCheckin, Solicitacao, Aplicacao


def profile(request, token):
    pessoa = Pessoa.objects.get(token=token)
    return render(request, 'checkins.html', dict(pessoa=pessoa))


@csrf_exempt
def checkin(request, tipo, token, token2=None):
    pessoa = None
    autorizado = True
    redirect_url = None
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    if tipo == 'pessoa' or tipo == 'ponto':
        if tipo == 'pessoa':
            pessoa = Pessoa.objects.get(token=token)
            redirect_url = '/profile/{}/'.format(pessoa.token)
            autorizado = pessoa.checar_dispositivo(request)
        elif tipo == 'ponto':
            ponto = PontoCheckin.objects.get(token=token)
            redirect_url = '/start/{}/'.format(ponto.token)
            pessoa = Pessoa.objects.get(aplicacao=ponto.aplicacao, token=token2)
        if request.POST:
            try:
                obj = pessoa.checkin(latitude, longitude, request.POST['image'][23:])
                return HttpResponse(json.dumps(dict(checkin=obj.uuid)))
            except ValidationError as e:
                return HttpResponse(json.dumps(dict(message=e.message)))

    elif tipo == 'solicitacao':
        solicitacao = Solicitacao.objects.filter(uuid=token).first()
        pessoa = solicitacao.pessoa
        if request.POST:
            solicitacao.latitude = latitude
            solicitacao.longitude = longitude
            solicitacao.data_hora_inicio = datetime.datetime.now()
            solicitacao.save()
            return HttpResponse(json.dumps(dict(solicitacao=solicitacao.uuid)))
    return render(request, 'checkin.html', dict(pessoa=pessoa, autorizado=autorizado, redirect_url=redirect_url))


def start(request, token):
    ponto = PontoCheckin.objects.get(token=token)
    return render(request, 'start.html', dict(ponto=ponto))


def end(request, uuid):
    checkin = Checkin.objects.get(uuid=uuid)
    return render(request, 'end.html', dict(checkin=checkin))


@csrf_exempt
def upload(request, uuid):
    solicitacao = Solicitacao.objects.get(uuid=uuid)
    if request.POST:
        solicitacao.salvar_imagens(request.POST)
        sucesso, mensagem = solicitacao.enviar_dados()
        if sucesso:
            solicitacao.save()
        return HttpResponse(mensagem)
    return render(request, 'upload.html', dict(solicitacao=solicitacao))


@csrf_exempt
def solicitar(request):
    token = request.POST['token']
    chave = request.POST['chave']
    descricao = request.POST['descricao']
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    imagens = {x: '' for x in request.POST['imagens'].split('|')}
    aplicacao = Aplicacao.objects.get(token_autenticacao=token)
    pessoa = Pessoa.objects.get(aplicacao=aplicacao, chave=chave)
    obj = Solicitacao(
        pessoa=pessoa, descricao=descricao,
        latitude=latitude, longitude=longitude, imagens=json.dumps(imagens)
    )
    obj.save()
    return HttpResponse(obj.uuid)
