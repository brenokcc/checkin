# Generated by Django 4.0.4 on 2022-06-14 19:16

from django.db import migrations, models
import sloth.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('checkin', '0002_pessoa_foto_alter_pessoa_chave'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkin',
            name='uuid',
            field=sloth.db.models.CharField(default=None, max_length=255, verbose_name='UUID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='checkin',
            name='imagem',
            field=models.ImageField(null=True, upload_to='checkin', verbose_name='Imagem'),
        ),
    ]
