# Generated by Django 4.0.4 on 2022-06-19 08:42

from django.db import migrations, models
import django.db.models.deletion
import sloth.core.base
import sloth.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('checkin', '0010_alter_checkin_data_hora'),
    ]

    operations = [
        migrations.CreateModel(
            name='Solicitacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', sloth.db.models.CharField(max_length=255, verbose_name='UUID')),
                ('descricao', sloth.db.models.CharField(max_length=255, verbose_name='Descrição')),
                ('latitude', sloth.db.models.CharField(blank=True, max_length=255, null=True, verbose_name='Latitude')),
                ('longitude', sloth.db.models.CharField(blank=True, max_length=255, null=True, verbose_name='Longitude')),
                ('data_hora_inicio', models.DateTimeField(blank=True, null=True, verbose_name='Data/Hora de Início')),
                ('data_hora_termino', models.DateTimeField(blank=True, null=True, verbose_name='Data/Hora de Término')),
                ('imagens', sloth.db.models.TextField(blank=True, default='{}', verbose_name='Imagens')),
                ('checkin', sloth.db.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='checkin.checkin', verbose_name='Checkin')),
                ('pessoa', sloth.db.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkin.pessoa', verbose_name='Pessoa')),
            ],
            options={
                'verbose_name': 'Solicitação',
                'verbose_name_plural': 'Solicitações',
            },
            bases=(models.Model, sloth.core.base.ModelMixin),
        ),
    ]
