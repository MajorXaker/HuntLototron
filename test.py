fields = ['kills', 'assists', 'deaths', 'primary_weapon', 'secondary_weapon', 'primary_ammo_A', 'primary_ammo_B', 'secondary_ammo_A', 'secondary_ammo_B']
commands_for_player = []
        
for command in fields:
    print ((type(command),command))
    # command = 'id_player_' + player + '_' + command_id
    # commands_for_player.append(command)