import re
import uuid
import json
import datetime
import requests
import geopy.distance
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from sloth.db import models, meta
import tempfile
import base64
try:
    import face_recognition
except ImportError:
    pass


class AplicacaoManager(models.Manager):
    def all(self):
        return self.role_lookups('Usuário', usuario='user').display('usuario', 'nome', 'get_qtd_pontos_checkin')


class Aplicacao(models.Model):
    usuario = models.CurrentUserField(verbose_name='Usuário')
    logo = models.ImageField(verbose_name='Logo', null=True, blank=True)
    nome = models.CharField(verbose_name='Nome')

    token_autenticacao = models.CharField(verbose_name='Token de Autenticação', null=True, blank=True)
    url_envio_dados = models.URLField(verbose_name='URL de Envio de Dados', null=True, blank=True)
    url_recebimento_dados = models.URLField(verbose_name='URL de Envio de Dados', null=True, blank=True)
    intervalo_envio_dados = models.IntegerField(verbose_name='Intervalo de Envio dos Dados', help_text='Tempo em minutos no qual os dados serão enviados para a aplicação.', default=60)
    intervalo_recebimento_dados = models.IntegerField(verbose_name='Intervalo de Recebimento dos Dados', help_text='Tempo em minutos no qual os dados serão recebidos da a aplicação.', default=1440)

    objects = AplicacaoManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.pontocheckin_set.exists():
            PontoCheckin(aplicacao=self, nome=self.nome).save()

    class Meta:
        icon = 'fullscreen'
        verbose_name = 'Aplicação'
        verbose_name_plural = 'Aplicações'
        fieldsets = {
            'Dados Gerais': ('nome', 'logo')
        }

    def __str__(self):
        return self.nome

    @meta('Qtd. de Pontos de Checkin')
    def get_qtd_pontos_checkin(self):
        return self.pontocheckin_set.count()

    def get_dados_gerais(self):
        return self.values(('nome')).image('logo')

    def get_dados_sincronizacao(self):
        return self.values('url_envio_dados', 'url_envio_dados', ('intervalo_envio_dados', 'intervalo_recebimento_dados'))

    def get_pontos_checkin(self):
        return self.pontocheckin_set.ignore('aplicacao').actions('Edit', 'Delete')

    def view(self):
        return self.values('get_dados_gerais', 'get_pontos_checkin').actions('Edit')

    def localizar_ponto_mais_proximo(self, latitude, longitude):
        ponto_mais_proximo = None
        for ponto in self.get_pontos_checkin().all():
            if ponto.latitude and ponto.longitude:
                if ponto_mais_proximo is None:
                    ponto_mais_proximo = ponto
                else:
                    d1 = ponto.calcular_distancia(latitude, longitude)
                    d2 = ponto_mais_proximo.calcular_distancia(latitude, longitude)
                    if d1 < d2:
                        ponto_mais_proximo = ponto
        return ponto_mais_proximo


class PontoCheckinManager(models.Manager):
    def all(self):
        return self


class PontoCheckin(models.Model):
    aplicacao = models.ForeignKey(Aplicacao, verbose_name='Aplicação')
    nome = models.CharField(verbose_name='Nome')

    latitude = models.CharField(verbose_name='Latitude', null=True, blank=True)
    longitude = models.CharField(verbose_name='Longitude', null=True, blank=True)
    raio = models.IntegerField(verbose_name='Raio de Abrangência', help_text='Distância em metros até onde será possível realizar auto check-in', null=True, blank=True)

    token = models.CharField(verbose_name='Token', null=True, blank=True)
    dispositivo = models.CharField(verbose_name='Dispositivo', null=True, blank=True)

    objects = PontoCheckinManager()

    class Meta:
        icon = 'pin-map'
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
        fieldsets = {
            'Dados Gerais': ('nome',),
            'Geolocalização': (('latitude','longitude'), 'raio')
        }

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid1().hex
        super().save(*args, **kwargs)

    @meta('Localização', 'geolocation')
    def get_localizacao(self):
        return self.latitude, self.longitude

    def has_get_localizacao_permission(self, user):
        return self.latitude and self.longitude

    @meta('URL', 'url')
    def get_url(self):
        return '{}/start/{}/'.format(settings.SITE_URL, self.token)

    @meta('QrCode', 'qrcode')
    def get_qrcode(self):
        return self.get_url()

    def get_dados_gerais(self):
        return self.values(('aplicacao', 'nome'), 'token')

    def get_dados_localizacao(self):
        return self.values(('latitude', 'longitude'), 'raio', 'get_localizacao')

    def get_dados_checkin(self):
        return self.values('get_url', 'get_qrcode')

    def view(self):
        return self.values('get_dados_gerais', 'get_dados_localizacao', 'get_dados_checkin')

    def calcular_distancia(self, latitude, longitude):
        coords_1 = (self.latitude, self.longitude)
        coords_2 = (latitude, longitude)
        distancia = geopy.distance.geodesic(coords_1, coords_2)
        return distancia.m


class PessoaManager(models.Manager):
    def all(self):
        return self.role_lookups(
            'Usuário', aplicacao__usuario='user'
        ).display(
            'get_foto', 'nome', 'chave', 'aplicacao'
        ).actions('SincronizarFoto')

    def sincronizar_fotos(self, atualizar=False):
        for pessoa in self.filter(foto__isnull=True).exclude(url__isnull=True):
            pessoa.sincronizar_foto(atualizar=atualizar)


class Pessoa(models.Model):
    aplicacao = models.ForeignKey(Aplicacao, verbose_name='Aplicação')
    nome = models.CharField(verbose_name='Nome')
    chave = models.CharField(verbose_name='Chave', help_text='Identificador da pessoa. Ex: E-mail, CPF, Matrícula.')
    foto = models.ImageField(verbose_name='Foto', upload_to='pessoa', null=True, blank=True)
    url = models.URLField(verbose_name='URL da Foto', null=True, blank=True)
    token = models.CharField(verbose_name='Token', null=True, blank=True)
    dispositivo = models.CharField(verbose_name='Dispositivo', null=True, blank=True)
    objects = PessoaManager()

    class Meta:
        icon = 'people'
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        fieldsets = {
            'Dados Gerais': ('aplicacao', ('nome', 'chave')),
            'Foto': ('foto', 'url')
        }

    def __str__(self):
        return self.nome

    @meta('Foto', 'photo')
    def get_foto(self):
        return self.foto

    def sincronizar_foto(self, atualizar=False):
        if self.url and (atualizar or not self.foto):
            nome_arquivo = self.url.split('/')[-1]
            resposta = requests.get(self.url)
            self.foto.save('{}{}'.format(self.id, nome_arquivo), ContentFile(resposta.content))

    def resetar_dispositivo(self):
        self.dispositivo = None
        self.save()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid1().hex
        super().save(*args, **kwargs)

    def get_dados_gerais(self):
        return self.values('nome', 'chave').image('foto')

    @meta('QrCode do Token', 'qrcode')
    def get_qrcode_token(self):
        return self.token

    @meta('URL', 'url')
    def get_url(self):
        return '{}/profile/{}/'.format(settings.SITE_URL, self.token)

    @meta('QrCode da URL', 'qrcode')
    def get_qrcode_url(self):
        return self.get_url()

    def get_dados_checkin(self):
        return self.values('token', 'get_qrcode_token', 'get_url', 'get_qrcode_url')

    def get_dados_dispositivo(self):
        return self.values('dispositivo').actions('ResetarDispositvo')

    def view(self):
        return self.values('get_dados_gerais', 'get_dados_checkin', 'get_dados_dispositivo', 'get_solicitacoes')

    def get_solicitacoes(self):
        return self.solicitacao_set.all().ignore('pessoa')

    def get_ultimos_checkins(self):
        return self.checkin_set.order_by('-id')[0:5]

    def comparar(self, imagem_base64):
        return True
        file_path = tempfile.mktemp(suffix='.jpeg')
        file = open(file_path, 'wb')
        file.write(base64.b64decode(imagem_base64))
        file.close()
        if1 = face_recognition.load_image_file(file_path)
        if2 = face_recognition.load_image_file(self.foto.path)
        fe1 = face_recognition.face_encodings(if1)
        fe2 = face_recognition.face_encodings(if2)
        if fe1 and fe2:
            result = face_recognition.compare_faces([fe1[0]], fe2[0])
            if result[0]:
                return True
        return False

    def checkin(self, latitude, longitude, imagem_base64, ponto=None):
        if self.comparar(imagem_base64):
            if ponto is None:
                ponto = self.aplicacao.localizar_ponto_mais_proximo(latitude, longitude)
            if ponto:
                obj = Checkin.objects.create(
                    uuid=uuid.uuid1().hex, pessoa=self, latitude=latitude, ponto=ponto,
                    longitude=longitude, data_hora=datetime.datetime.now()
                )
                return obj
            raise ValidationError('Ponto de checkin inválido.')
        raise ValidationError('Identificação facial não realizada.')

    def checar_dispositivo(self, request):
        user_agent = request.headers['User-Agent']
        if self.dispositivo is None and 'whatsapp' not in user_agent.lower():
            self.dispositivo = base64.b64encode(re.sub(r'\d|\(|\)', '.', user_agent).encode()).decode()
            self.save()
        if self.dispositivo:
            x = base64.b64decode(self.dispositivo.encode()).decode()
            return bool(re.search(x, user_agent))
        return True

class CheckinManager(models.Manager):
    def all(self):
        return self


class Checkin(models.Model):
    uuid = models.CharField(verbose_name='UUID')
    ponto = models.ForeignKey(PontoCheckin, verbose_name='Ponto', null=True, blank=True)
    pessoa = models.ForeignKey(Pessoa, verbose_name='Pessoa')
    data_hora = models.DateTimeField(verbose_name='Data/Hora', auto_created=True)
    latitude = models.CharField(verbose_name='Latitude')
    longitude = models.CharField(verbose_name='Longitude')
    imagem = models.ImageField(verbose_name='Imagem', upload_to='checkin', null=True)
    data_hora_sincronizacao = models.DateTimeField('Data/Hora da Sincronização', null=True, blank=True)

    objects = CheckinManager()

    class Meta:
        icon = 'pin-map'
        verbose_name = 'Checkin'
        verbose_name_plural = 'Checkin'

    def __str__(self):
        return 'Checkin {}'.format(self.pk)

    @meta('Localização', 'geolocation')
    def get_localizacao(self):
        return self.latitude, self.longitude

    @meta('Distância do Ponto')
    def get_distancia_ponto(self):
        if self.ponto:
            return self.ponto.calcular_distancia(self.latitude, self.longitude)
        return None

    def view(self):
        return self.values('uuid', ('pessoa', 'data_hora'), ('latitude', 'longitude'), 'get_localizacao', ('ponto', 'get_distancia_ponto'))


class SolicitacaoManager(models.Manager):
    def all(self):
        return self.display('uuid', 'pessoa', 'descricao')

    def pendentes(self):
        return self.filter(data_hora_termino__isnull=True)


class Solicitacao(models.Model):
    uuid = models.CharField(verbose_name='UUID')
    pessoa = models.ForeignKey(Pessoa, verbose_name='Pessoa')
    descricao = models.CharField(verbose_name='Descrição')
    latitude = models.CharField(verbose_name='Latitude', null=True, blank=True)
    longitude = models.CharField(verbose_name='Longitude', null=True, blank=True)
    data_hora_inicio = models.DateTimeField(verbose_name='Data/Hora de Início', null=True, blank=True)
    data_hora_termino = models.DateTimeField(verbose_name='Data/Hora de Término', null=True, blank=True)
    imagens = models.TextField(verbose_name='Imagens', blank=True, default='{}')

    objects = SolicitacaoManager()

    class Meta:
        verbose_name = 'Solicitação'
        verbose_name_plural = 'Solicitações'
        fieldsets = {
            'Dados Gerais': ('pessoa', 'descricao'),
            'Imagens': ('imagens',)
        }

    def __str__(self):
        return self.descricao

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid1().hex
        super().save(*args, **kwargs)

    def salvar_imagens(self, dados):
        imagens = json.loads(self.imagens)
        for descricao in imagens:
            imagens[descricao] = dados[descricao][23:]
        self.imagens = json.dumps(imagens)
        self.data_hora_termino = datetime.datetime.now()
        self.save()

    def get_descricoes_imagens(self):
        return json.loads(self.imagens).keys()

    def reiniciar(self):
        self.data_hora_inicio = None
        self.data_hora_termino = None
        self.save()

    def get_dados_gerais(self):
        return self.values('uuid', 'pessoa', ('latitude', 'longitude'), ('data_hora_inicio', 'data_hora_termino'))

    def get_dados_imagens(self):
        return self.values('imagens')

    def view(self):
        return self.values('get_dados_gerais', 'get_dados_imagens').actions('ReiniciarSolicitacao')
