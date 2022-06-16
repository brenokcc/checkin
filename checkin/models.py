import uuid
import requests
from django.core.files.base import ContentFile
from sloth.db import models, meta


class AplicacaoManager(models.Manager):
    def all(self):
        return self.role_lookups('Usuário', usuario='user')


class Aplicacao(models.Model):
    usuario = models.CurrentUserField(verbose_name='Usuário')
    nome = models.CharField(verbose_name='Nome')
    token = models.CharField(verbose_name='Token')
    redirect = models.URLField(verbose_name='Redirecionamento')

    objects = AplicacaoManager()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid1().hex
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Aplicação'
        verbose_name_plural = 'Aplicações'
        fieldsets = {
            'Dados Gerais': ('nome', 'redirect')
        }

    def __str__(self):
        return self.nome



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

    def view(self):
        return super().view().actions('ResetarDispositvo')


class CheckinManager(models.Manager):
    def all(self):
        return self


class Checkin(models.Model):
    uuid = models.CharField(verbose_name='UUID')
    pessoa = models.ForeignKey(Pessoa, verbose_name='Pessoa')
    data_hora = models.DateField(verbose_name='Data/Hora', auto_created=True)
    latitude = models.CharField(verbose_name='Latitude')
    longitude = models.CharField(verbose_name='Latitude')
    imagem = models.ImageField(verbose_name='Imagem', upload_to='checkin', null=True)

    objects = CheckinManager()

    class Meta:
        verbose_name = 'Checkin'
        verbose_name_plural = 'Checkin'

    def __str__(self):
        return 'Checkin {}'.format(self.pk)
