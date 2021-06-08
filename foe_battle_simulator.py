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

import random
from time import sleep
from sys import stdout
from itertools import cycle
from enum import Enum, auto
from math import floor

class Player:
    def __init__(self, name, army, boost_attack=0, boost_defense=0, chance_ao=0):
        self.name = name
        self.army = army
        self.boost_attack = boost_attack
        self.boost_defense = boost_defense
        self.chance_ao = chance_ao

class Unit:
    class Class(Enum):
        HEAVY     = auto()
        LIGHT     = auto()
        FAST      = auto()
        ARTILLERY = auto()
        RANGED    = auto()

    def __init__(self, unit_class, attack, defense, range, movement, skills={}, health=10):
        self.attack   = attack
        self.defense  = defense
        self.range    = range
        self.movement = movement
        self.skills   = skills
        self.health   = health
        self.type     = type(self)
        self.unit_class = unit_class
        
    def __repr__(self):
        attack_defense = str(self.attack) + '/' + str(self.defense)
        if self.has_revealed_identity():
            attack_defense = '*' + attack_defense + '*'
        if hasattr(self, 'position'):
            attack_defense = str(self.position) + '/' + attack_defense
        return type(self).__name__ + '(' + attack_defense + '/' + str(self.health) + ')'
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def has_secret_identity(self):
        # return 'secret_identity' in self.skills and self.skills['secret_identity'] is True
        return False

    def has_revealed_identity(self):
        # return 'secret_identity' in self.skills and self.skills['secret_identity'] is False
        return False

    def reveal_secret_identity(self, possible_prototypes):
        return False

    def bonus_attack(self, opponent):
        return 0

    def bonus_defense(self, opponent):
        return 0

class SteelWarden(Unit):
    def __init__(self):
        super().__init__(Unit.Class.HEAVY, 400, 600, 7, 18, {'keen_eye':20, 'force_field':2})

    def bonus_attack(self, opponent):
        if opponent.unit_class is Unit.Class.FAST:
            return 250
        if opponent.unit_class is Unit.Class.RANGED:
            return 250
        return 0

    def bonus_defense(self, opponent):
        if opponent.unit_class is Unit.Class.FAST:
            return 250
        if opponent.unit_class is Unit.Class.RANGED:
            return 250
        return 0

class NailStorm(Unit):
    def __init__(self):
        super().__init__(Unit.Class.RANGED, 650, 650, 16, 14, {'keen_eye':25})

    def bonus_attack(self, opponent):
        if opponent.unit_class is Unit.Class.LIGHT:
            return 300
        if opponent.unit_class is Unit.Class.ARTILLERY:
            return 300
        return 0

    def bonus_defense(self, opponent):
        if opponent.unit_class is Unit.Class.LIGHT:
            return 300
        if opponent.unit_class is Unit.Class.ARTILLERY:
            return 300
        return 0

class EnergyCannon(Unit):
    def __init__(self):
        super().__init__(Unit.Class.FAST, 800, 900, 8, 30, {'keen_eye':30})

    def bonus_attack(self, opponent):
        if opponent.unit_class is Unit.Class.ARTILLERY:
            return 350
        if opponent.unit_class is Unit.Class.RANGED:
            return 350
        return 0

    def bonus_defense(self, opponent):
        if opponent.unit_class is Unit.Class.ARTILLERY:
            return 350
        if opponent.unit_class is Unit.Class.RANGED:
            return 350
        return 0

class Rogue(Unit):
    def __init__(self):
        super().__init__(Unit.Class.LIGHT, 100, 1, 1, 14, {'secret_identity':True})

    def has_secret_identity(self):
        return self.skills['secret_identity']

    def has_revealed_identity(self):
        return self.skills['secret_identity'] is False

    def reveal_secret_identity(self, possible_prototypes):
        if self.skills['secret_identity'] is False:
            return False

        prototypes = [u for u in possible_prototypes if not u.has_secret_identity()]
        if not len(prototypes):
            return False

        prototype = random.choice(prototypes).type()
        self.unit_class = prototype.unit_class
        self.attack   = prototype.attack
        self.defense  = prototype.defense
        self.range    = prototype.range
        self.movement = prototype.movement
        self.skills   = prototype.skills
        self.type     = prototype.type
        self.skills['secret_identity'] = False
        # print(self, 'revealed as', prototype)
        return True

def wave_to_str(wave, attacker, defender):
    fg_black = u'\u001b[30m'
    fg_red = u'\u001b[31m'
    fg_green = u'\u001b[32m'
    bg_yellow = u'\u001b[43m'
    reset = u'\u001b[0m'

    to_str = ''
    for unit in wave:
        colors = ''
        if unit is defender:
            colors = colors + fg_black + bg_yellow
        elif unit is attacker:
            colors = colors + fg_green + bg_yellow
        if unit.health <= 0:
            colors = colors + fg_red
        to_str += colors + str(unit).rjust(27) + reset
    return to_str

def battle_layout(attacker, defender):
    fg_black = u'\u001b[30m'
    fg_red = u'\u001b[31m'
    fg_green = u'\u001b[32m'
    bg_yellow = u'\u001b[43m'
    reset = u'\u001b[0m'

    to_str=''
    for i in range(-7, 8):
        if attacker and attacker.position == i:
            if defender and defender.position == i:
                to_str += fg_green + bg_yellow + 'a' + ' / ' + fg_black + bg_yellow + 'd' + reset
            else:
                to_str += fg_green + bg_yellow + 'attacker'.center(8) + reset
        else:
            if defender and defender.position == i:
                to_str += fg_black + bg_yellow + 'defender'.center(8) + reset
            else:
                to_str += str(i).center(8)
    return to_str

def sort_for_drawing(units):
    def weight_drawing(u):
        if u.has_secret_identity():
            return 11
        elif 'rapid_deployment' in u.skills and u.skills['rapid_deployment']:
            return -1
        else:
            return u.health
    random.shuffle(units)
    units.sort(key=weight_drawing)

def pop_defender(possible_defenders):
    def weight_targeting(u):
        if u.has_secret_identity():
            return -1
        else:
            return u.health

    defenders = []
    lowest_weight = 11
    for u in possible_defenders:
        weight = weight_targeting(u)
        if weight == lowest_weight:
            defenders.append(u)
        elif weight < lowest_weight:
            defenders = [u]
            lowest_weight = weight

    defender = random.choice(defenders)
    possible_defenders.remove(defender)

    return defender

def fight(p, c, verbose=False, delay=False, movement_cost=3):
    def distance(x, y):
        return abs(x-y)
    for p_wave in p.army:
        for c_wave in c.army:
            # print('########################' + ' new wave ' + '########################')
            units_waiting = p_wave | c_wave
            # hide identities of all agents
            with Rogue() as unrevealed:
                for u in units_waiting:
                    if type(u) is type(unrevealed):
                        # unreveal secret identity of rogue, only health is kept, the rest is copied
                        u.base_attack   = u.attack   = unrevealed.attack
                        u.base_defense  = u.defense  = unrevealed.defense
                        u.base_range    = u.range    = unrevealed.range
                        u.base_movement = u.movement = unrevealed.movement
                        u.base_skills   = u.skills   = unrevealed.skills

            # reset units to start position
            for unit in p_wave:
                # left most
                unit.position = -7
            for unit in c_wave:
                # right most
                unit.position = 7

            # who is drawing first?
            units_waiting = list(units_waiting)
            sort_for_drawing(units_waiting)
            pool = cycle(units_waiting)

            for attacker in pool:
                if attacker.health == 0:
                    continue

                move_max = floor(attacker.movement/movement_cost)
                if attacker in p_wave:
                    chance_ao = p.chance_ao
                    boost_attack = p.boost_attack

                    defenders = [unit for unit in c_wave
                            if unit.health > 0 and (move_max + attacker.range) >= distance(unit.position, attacker.position)]
                    boost_defense = c.boost_defense
                    # moves right (to positive values)
                    move_direction = 1
                elif attacker in c_wave:
                    chance_ao = 0
                    boost_attack = c.boost_attack
                    boost_attack = c.boost_attack

                    defenders = [unit for unit in p_wave
                            if unit.health > 0 and (move_max + attacker.range) >= distance(unit.position, attacker.position)]
                    boost_defense = p.boost_defense
                    # moves left (to negative values)
                    move_direction = -1
                else:
                    print('panic')
                    exit(1)

                if not defenders:
                    if attacker.position == move_direction*7:
                        if verbose:
                            print(wave_to_str(p_wave, None, None))
                            print(wave_to_str(c_wave, None, None))
                        break
                    else:
                        attacker.position += move_direction * move_max
                        if attacker.position < -7:
                            attacker.position = -7
                        elif attacker.position > 7:
                            attacker.position = 7

                        print(wave_to_str(p_wave, attacker, None))
                        print(wave_to_str(c_wave, attacker, None))
                        print(battle_layout(attacker, None))
                        stdout.write(u"\u001b[1000D") # Move left
                        stdout.write(u"\u001b[" + str(3) + "A") # Move up
                        if delay:
                            input()
                            stdout.write(u"\u001b[" + str(1) + "A") # Move up
                        continue

                defender = pop_defender(defenders)

                # move into range
                if distance(attacker.position, defender.position) > attacker.range:
                    attacker.position += move_direction * (distance(attacker.position, defender.position) - attacker.range)

                # calculate damage based on https://youtu.be/ksX0w1h4-4U?t=25
                attack  = (attacker.attack  + attacker.bonus_attack(defender))  * (100 + boost_attack)  / 100
                defense = (defender.defense + defender.bonus_defense(attacker)) * (100 + boost_defense) / 100
                if defense == 0:
                    q = 0
                else:
                    q = attack/defense

                if q >= 20:
                    min_damage = 10
                elif q >= 10:
                    min_damage = 9
                elif q >= 3.5:
                    min_damage = 8
                elif q >= 2.3:
                    min_damage = 7
                elif q >= 1.8:
                    min_damage = 6
                elif q >= 1.3:
                    min_damage = 5
                elif q >= 1:
                    min_damage = 4
                elif q >= 0.7:
                    min_damage = 3
                elif q >= 0.4:
                    min_damage = 2
                elif q >= 0.1:
                    min_damage = 1
                else:
                    min_damage = 0

                if q >= 10:
                    max_damage = 10
                elif q >= 3.1:
                    max_damage = 9
                elif q >= 1.8:
                    max_damage = 8
                elif q >= 1.2:
                    max_damage = 7
                elif q >= 0.9:
                    max_damage = 6
                elif q >= 0.6:
                    max_damage = 5
                elif q >= 0.3:
                    max_damage = 4
                elif q >= 0.2:
                    max_damage = 3
                elif q >= 0.1:
                    max_damage = 2
                else:
                    max_damage = 0

                if 'force_field' in defender.skills:
                    if max_damage > 0:
                        if max_damage > defender.skills['force_field']:
                            max_damage = max_damage - defender.skills['force_field']
                        else:
                            max_damage = 1
                    if min_damage > 0:
                        if min_damage > defender.skills['force_field']:
                            min_damage = min_damage - defender.skills['force_field']
                        else:
                            min_damage = 1

                if random.random() < (chance_ao / 100):
                    #print('AO hit')
                    max_damage = int(round(max_damage * 1.5))
                    min_damage = int(round(min_damage * 1.5))

                damage = random.randint(min_damage, max_damage)

                if 'keen_eye' in attacker.skills and random.random() < (attacker.skills['keen_eye'] / 100):
                    #print('keen eye hit')
                    damage = damage * 2

                if damage < defender.health:
                    defender.health -= damage
                    # TODO retaliate...
                else:
                    if not defender.reveal_secret_identity(defenders):
                        defender.health = 0

                if verbose:
                    print(wave_to_str(p_wave, attacker, defender))
                    print(wave_to_str(c_wave, attacker, defender))
                    print(battle_layout(attacker, defender))
                    stdout.write(u"\u001b[1000D") # Move left
                    stdout.write(u"\u001b[" + str(3) + "A") # Move up
                if delay:
                    input()
                    stdout.write(u"\u001b[" + str(1) + "A") # Move up

if __name__ == "__main__":
    player = Player('player',
            [{SteelWarden(), SteelWarden(), Rogue(), Rogue(), Rogue(), Rogue(), Rogue(), Rogue()}],
            boost_attack = 840,
            boost_defense = 664,
            chance_ao = 27.05)
    computer = Player('computer',
            [{SteelWarden(), SteelWarden(), SteelWarden(), SteelWarden(), SteelWarden(), SteelWarden(), SteelWarden(), SteelWarden()},
                {SteelWarden(), SteelWarden(), SteelWarden(), SteelWarden()}],
            boost_attack = 827, # attrition 63
            boost_defense = 827)
    fight(player, computer, verbose=True, delay=True)
