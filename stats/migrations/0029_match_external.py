# Generated by Django 4.0.2 on 2022-02-14 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0028_remove_match_bounty_match_player_1_bounty_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='external',
            field=models.BooleanField(default=False, verbose_name='Externally added match'),
        ),
    ]