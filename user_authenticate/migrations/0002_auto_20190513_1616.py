# Generated by Django 2.2.1 on 2019-05-13 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_authenticate', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(),
        ),
    ]
