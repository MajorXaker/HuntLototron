# Generated by Django 4.0 on 2021-12-27 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roulette', '0010_weapon_is_ammo_b'),
    ]

    operations = [
        migrations.RenameField(
            model_name='weapon',
            old_name='is_ammo_B',
            new_name='has_ammo_B',
        ),
    ]