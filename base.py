# sample implementation

class BaseObj:
    '''Base class for all objects in tactics ogre'''

    def __init__(self, stats=None, extras=None, name=None):
        '''
        Parameters
        ----------
        stats : List[int]
            [str, vit, dex]
            Stats from equipement or a character.
            Current implementation integrates the class into a character.
        extras : List[int]
            [atk, def_]
            ATK and DEF from equipement or a class.
        name : string
            Name of the object.
        '''
        self.name = name
        stats_fields = ['str', 'vit', 'dex']
        extras_fields = ['atk', 'def_']
        
        stats =  stats if stats is not None else [0]*len(stats_fields)
        extras = extras if extras is not None else [0]*len(extras_fields)
        if isinstance(extras, int):
            extras = [extras]*len(extras_fields)

        for field, value in zip(stats_fields, stats):
            setattr(self, field, value)
        for field, value in zip(extras_fields, extras):
            setattr(self, field, value)

class Equipment(BaseObj):
    def __init__(self, etype='str', dtype=None, **params):
        '''
        Parameters
        ----------
        etype : {'str', 'dex', 'shield', 'armor', 'jewelry'}
            Equipment type.
        dtype : List[int] or Dict[str, int]
            [crush, slash, pierce]
            Note that inputing 20 is considered as 20%.
            Damage type bonuses or resistance.
        '''
        super().__init__(**params)
        self.etype = etype
        if etype in {'str', 'dex'}:
            if self.atk <= 0:
                raise ValueError('Invalid weapon atk')
            self.atk *= 1.2
            # special weapons with def are not considered
            self.def_ = 0
        elif etype.startswith('sh'):
            if self.def_ <= 0:
                raise ValueError('Invalid shield def')
            self.def_ *= 0.9
            # temporary atk of shield are not considered
            self.atk = 0
        elif etype.startswith('a'):
            # recall that extras = [extras]*len(extras_fields)
            if self.atk == self.def_:
                self.atk = 0

        # elemental and racial bonuses are not considered yet
        damage_types_fields = ['c', 's', 'p']  # crush, slash, pierce
        dtype = dtype if dtype is not None else [0]*len(damage_types_fields)
        if isinstance(dtype, list):
            self.damage_types = {field: value/100 for field, value in zip(damage_types_fields, dtype)}
        elif isinstance(dtype, dict):
            self.damage_types = {f: 0 for f in damage_types_fields}
            self.damage_types.update({k: v/100 for k, v in dtype.items()})

    def __repr__(self):
        # not finished
        return self.name
                
class Unit(BaseObj):

    def __init__(self, equipment=None, **params):
        '''
        Dual wielding is not considered yet.

        Parameters
        ----------
        equipment : List[Equipment]
            The first piece of the equipment is the weapon.
        '''
        super().__init__(**params)
        self.equipment = equipment if equipment is not None else [Equipment()]

    @property
    def offense(self):
        if self.equipment[0].etype == 'str':
            return (0.9*self.str + 0.7*self.dex
                    + 0.7*sum(item.str for item in self.equipment)
                    + 0.5*sum(item.dex for item in self.equipment))
        elif self.equipment[0].etype == 'dex':
            return (0.7*self.str + 1.1*self.dex
                    + 0.5*sum(item.str for item in self.equipment)
                    + 0.9*sum(item.dex for item in self.equipment))
        else:
            raise ValueError(f'Invalid weapon type, got {self.equipment[0].etype}')

    @property
    def toughness(self):
        return (0.7*self.str + 1.1*self.vit
                + 0.5*sum(item.str for item in self.equipment)
                + 0.9*sum(item.vit for item in self.equipment))

    @property
    def damage_type(self):
        for dtype, value in self.equipment[0].damage_types.items():
            if value > 0:
                return dtype
        raise ValueError(f'Invalid weapon damage type')

    @property
    def extra_damage(self):
        return sum(item.atk for item in self.equipment) + self.atk

    @property
    def defense(self):
        return sum(item.def_ for item in self.equipment) + self.def_

    def attack(self, target, base_correction=0, mul_correction=0):
        '''
        Parameters
        ----------
        target : Unit
            Attacking target.
        base_correction : int
            Temporary measure to accommodate base damage from skills.
            Weapon skills and elemental augments add 4 damage or 3 defense per rank;
            racial skills add 5 damage per rank.
        mul_correction : float
            Temporary measure to accommodate elemental and racial bonuses.
        '''
        offense = self.offense + base_correction
        toughness = target.toughness
        dmg_bonus = self.equipment[0].damage_types[self.damage_type] + mul_correction
        resistance = sum(item.damage_types[self.damage_type] for item in target.equipment if item.etype not in {'str', 'dex'})
        extra_dmg = self.extra_damage
        defense = target.defense
        base_dmg = offense - toughness
        base_mul = min(max(1+dmg_bonus-resistance, 0), 2.5)
        scaled_base_dmg = base_dmg * base_mul

        print()
        print(f'{self.name} attacks {target.name}')
        print(f'offense: \t{offense}')
        print(f'toughness: \t{toughness}')
        print(f'dmg bonus: \t{dmg_bonus}')
        print(f'resistance: \t{resistance}')
        print(f'base dmg: \t{base_dmg: .1f} (*{base_mul: .2f}={scaled_base_dmg: .1f})')
        print(f'extra dmg: \t{extra_dmg: .1f}')
        print(f'defense: \t{defense}')
        print(f'final dmg: \t{int(max(1, scaled_base_dmg+extra_dmg-defense))}')

axe = Equipment(name='Poleaxe',
                extras=119,
                dtype={'s': 18})
light_armor = Equipment('a',
                        name='Plated Vest',
                        extras=33,
                        dtype=[21, 15, 21])
acc_helm = Equipment('a',
                      name='Burgonet',
                      extras=19,
                      dtype=[11, 8, 11])
a_ring = Equipment('j',
                   extras=[5, 0])
ber = Unit([axe, light_armor, acc_helm, a_ring],
            stats=[104, 75, 96],
            extras=[22, 11],
            name='berserker')

bow = Equipment('dex',
                name='Silver Arch',
                extras=61,
                dtype={'p': 3})
light_shield = Equipment('sh',
                         name='Baldur Shield',
                         extras=18,
                         dtype=[11, 8, 11])
light_leg = Equipment('a',
                      name='Scale Leggings',
                      extras=19,
                      dtype=[11, 8, 11])
dex_ring = Equipment('j',
                     stats=[0, 0, 10],
                     extras=[5, 0])
archer = Unit([bow, light_leg, light_shield, dex_ring, light_armor],
              extras=[11, 5],
              stats=[81, 66, 107],
              name='archer')

archer.attack(ber, 24)
ber.attack(archer, 28)


'''
sword = Equipment('str', name='sample_sword',
                  stats=[100, 0, 0], extras=[100, 0], dtype=[10, 0, 0])
item = Equipment('armor', name='sample_item',
                  stats=[0, 0, 100])
denam = Unit([sword, item], stats=[100, 100, 100])
print(denam.offense)
denam.attack(denam)
'''
