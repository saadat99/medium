# Generated by Django 2.1.9 on 2019-06-17 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='posts',
            options={'verbose_name_plural': 'Posts'},
        ),
        migrations.AddField(
            model_name='posts',
            name='auther',
            field=models.CharField(default='saadat', max_length=200),
            preserve_default=False,
        ),
    ]
