# Generated by Django 4.0 on 2021-12-25 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0022_alter_player_also_known_as'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='hash_key',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Hash key of this user.'),
        ),
        migrations.AddField(
            model_name='player',
            name='hash_redeemable',
            field=models.BooleanField(default=False, verbose_name='Restriction. No one should be able to bind a real account.'),
        ),
        migrations.AddField(
            model_name='player',
            name='show_tooltips',
            field=models.BooleanField(default=True, verbose_name='States whether tooltips and usage hints are visible.'),
        ),
    ]