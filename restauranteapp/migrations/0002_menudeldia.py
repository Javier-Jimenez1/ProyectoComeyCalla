# Generated by Django 5.2 on 2025-06-01 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restauranteapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuDelDia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True, unique=True)),
                ('platos', models.ManyToManyField(to='restauranteapp.plato')),
            ],
        ),
    ]
