# Generated by Django 4.0 on 2021-12-18 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0011_match_player_1_signature_match_player_2_signature'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='player_3_signature',
            field=models.BooleanField(blank=True, default=False, verbose_name='player 2 signature'),
        ),
    ]
