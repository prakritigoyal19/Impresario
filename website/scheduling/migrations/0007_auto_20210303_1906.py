# Generated by Django 3.0.11 on 2021-03-03 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0006_auto_20210303_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='eventId',
            field=models.TextField(),
        ),
    ]