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

    class Meta:
        verbose_name = 'Aplicação'
        verbose_name_plural = 'Aplicações'

    def __str__(self):
        return self.nome



class PessoaManager(models.Manager):
    def all(self):
        return self.role_lookups('Usuário', aplicacao__usuario='user').display('get_foto', 'nome', 'chave', 'aplicacao')


class Pessoa(models.Model):
    aplicacao = models.ForeignKey(Aplicacao, verbose_name='Aplicação')
    nome = models.CharField(verbose_name='Nome')
    chave = models.CharField(verbose_name='Chave', help_text='Identificador da pessoa. Ex: E-mail, CPF, Matrícula.')
    foto = models.ImageField(verbose_name='Foto', upload_to='pessoa')

    objects = PessoaManager()

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'

    def __str__(self):
        return self.nome

    @meta('Foto', 'photo')
    def get_foto(self):
        return self.foto


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
