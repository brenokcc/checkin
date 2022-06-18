# Generated by Django 4.0.4 on 2022-06-18 15:31

from django.db import migrations, models
import sloth.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('checkin', '0007_pontocheckin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aplicacao',
            name='redirect',
        ),
        migrations.RemoveField(
            model_name='aplicacao',
            name='token',
        ),
        migrations.AddField(
            model_name='aplicacao',
            name='intervalo_envio_dados',
            field=models.IntegerField(default=60, help_text='Tempo em minutos no qual os dados serão enviados para a aplicação.', verbose_name='Intervalo de Envio dos Dados'),
        ),
        migrations.AddField(
            model_name='aplicacao',
            name='intervalo_recebimento_dados',
            field=models.IntegerField(default=1440, help_text='Tempo em minutos no qual os dados serão recebidos da a aplicação.', verbose_name='Intervalo de Recebimento dos Dados'),
        ),
        migrations.AddField(
            model_name='aplicacao',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Logo'),
        ),
        migrations.AddField(
            model_name='aplicacao',
            name='token_autenticacao',
            field=sloth.db.models.CharField(blank=True, max_length=255, null=True, verbose_name='Token de Autenticação'),
        ),
        migrations.AddField(
            model_name='aplicacao',
            name='url_envio_dados',
            field=models.URLField(blank=True, null=True, verbose_name='URL de Envio de Dados'),
        ),
        migrations.AddField(
            model_name='aplicacao',
            name='url_recebimento_dados',
            field=models.URLField(blank=True, null=True, verbose_name='URL de Envio de Dados'),
        ),
        migrations.AddField(
            model_name='checkin',
            name='data_hora_sincronizacao',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data/Hora da Sincronização'),
        ),
        migrations.AlterField(
            model_name='pontocheckin',
            name='raio',
            field=models.IntegerField(blank=True, help_text='Distância em metros até onde será possível realizar auto check-in', null=True, verbose_name='Raio de Abrangência'),
        ),
    ]
