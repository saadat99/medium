# Generated by Django 2.2.4 on 2019-08-03 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_posts_auther'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='auther',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]