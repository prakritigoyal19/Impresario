# Generated by Django 3.0.11 on 2021-03-03 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0004_auto_20210303_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event', to='scheduling.Organization'),
        ),
    ]
