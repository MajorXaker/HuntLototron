# Generated by Django 3.2.9 on 2021-12-09 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roulette', '0007_slots_weight'),
    ]

    operations = [
        migrations.RenameField(
            model_name='layout',
            old_name='chance',
            new_name='weight',
        ),
    ]
