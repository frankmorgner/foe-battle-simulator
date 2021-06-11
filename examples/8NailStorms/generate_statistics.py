#
# Copyright (c) 2021 Frank Morgner
#
# This file is part of FoE Battle Simulator.
#
# FoE Battle Simulator is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# FoE Battle Simulator is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# FoE Battle Simulator.  If not, see <http://www.gnu.org/licenses/>.
#
import os, sys
directory = os.path.dirname( __file__ )
sys.path.append(os.path.abspath(os.path.join(directory, os.pardir)))
sys.path.append(os.path.abspath(os.path.join(directory, os.pardir, os.pardir)))

from foe_battle_simulator import *
import progress

chance_ao_step = 10
chance_ao_max = 40
player_defense_step = 10
player_defense_max = 1600
player_attack_step = 10
player_attack_max = 1600
computer_attack = 827  # attrition 63
computer_defense = 827 # attrition 63
retries = 100

chance_ao = chance_ao_max

total = (chance_ao_max*player_attack_max*player_defense_max*retries)/(chance_ao_step*player_attack_step*player_defense_step)
done = 0
while 0 < chance_ao:
    chance_ao = chance_ao - chance_ao_step
    filename = 'a'+str(computer_attack)+'_d'+str(computer_defense)+'_ao'+str(chance_ao)
    f_wins = open(os.path.join(directory, filename+'.txt'), 'w')
    f_wins.write(f'# AO chance {chance_ao}\n')
    f_wins.write( '# att   def     wins   units lost\n')
    with open(os.path.join(directory, filename+'_wins.gp'), 'w') as f:
        f.write(
f"""set xlabel 'Player Attack'
set ylabel 'Player Defense'
set zlabel 'Total Wins'
set title '8 Nail Storms vs 8 Nail Storms'
set terminal svg size 500,500
set output '{filename}.svg'

plot '{filename}.txt' u 1:2:3 with image""")
        f.close()
    player_attack = player_attack_max
    while 0 <= player_attack:
        player_defense = player_defense_max
        while 0 <= player_defense:
            total_wins = 0
            total_units_lost = 0
            n = retries
            while 0 < n:
                done += 1
                progress.progress(done, total, status=f'{player_attack:>4}/{player_defense:<4} AO {chance_ao:<2}%')
                player = Player('player',
                        [{NailStorm(), NailStorm(), NailStorm(), NailStorm(), NailStorm(), NailStorm(), NailStorm(), NailStorm()}],
                        boost_attack = player_attack,
                        boost_defense = player_defense,
                        chance_ao = chance_ao)
                computer = Player('computer',
                        [{NailStorm(), NailStorm(), NailStorm(), NailStorm(), NailStorm(), NailStorm(), NailStorm(), NailStorm()}],
                        boost_attack = 827, # attrition 63
                        boost_defense = 827)

                p_units = 0
                for wave in player.army:
                    p_units = p_units + len(wave)

                fight(player, computer, map_scaling=1.5)

                p_units_left = 0
                for wave in player.army:
                    for u in wave:
                        if u.health == 0:
                            total_units_lost = total_units_lost + 1
                        else:
                            p_units_left = p_units_left + 1
                if p_units_left > 0:
                    total_wins = total_wins + 1
                n = n - 1

            f_wins.write(f'{player_attack:5d} {player_defense:5d} {total_wins:7d} {total_units_lost:7d}\n')

            player_defense = player_defense - player_defense_step
        player_attack = player_attack - player_attack_step

    f_wins.close()
