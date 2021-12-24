# Generated by Django 4.0 on 2021-12-24 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0018_remove_player_asissts_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='allow_see_mathes',
            field=models.BooleanField(default=False, verbose_name='Allow other users see your matches.'),
        ),
        migrations.AddField(
            model_name='player',
            name='allow_see_name',
            field=models.BooleanField(default=False, verbose_name='Allow other users see your matches and your name.'),
        ),
        migrations.AddField(
            model_name='player',
            name='see_only_my_matches',
            field=models.BooleanField(default=True, verbose_name='Display only matches, where you have participated.'),
        ),
    ]
