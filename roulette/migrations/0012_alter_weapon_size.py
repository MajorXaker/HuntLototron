# Generated by Django 4.0 on 2021-12-27 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roulette', '0011_rename_is_ammo_b_weapon_has_ammo_b'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weapon',
            name='size',
            field=models.IntegerField(choices=[(1, 'Small - 1'), (2, 'Medium - 2'), (3, 'Large - 3')]),
        ),
    ]
