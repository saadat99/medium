# Generated by Django 2.2.4 on 2019-08-03 21:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20190804_0212'),
    ]

    operations = [
        migrations.RenameField(
            model_name='posts',
            old_name='auther',
            new_name='author',
        ),
    ]