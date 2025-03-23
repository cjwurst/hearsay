from hearsay.components import Component
from custom_components.minion_components import *
from custom_components.card_components import *
        
"""An object composed of components which grant it behavior."""
class Entity:
    # The constructor should not be called directly (usually). Use Entity.Builder instead.
    def __init__(self, event_director, *components:Component):
        self.id = id(self)
        self._components = []
        self.attach_components(event_director, *components)

    # TODO: set newly attached components state to current state
    def attach_components(self, event_director, *components:Component):
        self._components += components
        for component in components:
            component.attach(event_director, self.id)

    # Note: not invertible!
    def destroy(self):
        for component in self._components:
            component.detach()

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 23:02:54 2022

@author: mczyk
"""

"""A class representing generic information that every card must have."""
class Card:
    def __init__(self) -> None:
        self.name = ""
        self.base_cost = -1
        self.current_cost = -1
        self.card_text = ""
        self.rarity = ""
        self.class_ = ""
        self.cardType = ""
        self.tribe = ""
        self.cardSet = ""

"""A class representing the unique attributes of a minion."""
class Minion(Card):
    def __init__(self) -> None:
        super().__init__()
        self.base_health = -1
        self.curent_health = -1
        self.max_health = -1
        
        self.base_attack = -1
        self.current_attack = -1

"""A class representing the unique attributes of a spell."""
class Spell(Card):
    def __init__(self) -> None:
        super().__init__()

"""A class representing the unique attributes of a hero."""
class Hero(Card):
    def __init__(self) -> None:
        super().__init__()
        self.armor = -1
        self.hero_power = None

"""A class representing the unique attributes of a hero power."""
class HeroPower:
    def __init__(self) -> None:
        self.name = ""
        self.base_cost = -1
        self.card_text = ""

"""A class representing the unique attributes of a weapon."""
class Weapon(Card):
    def __init__(self) -> None:
        super().__init__()
        self.base_attack = 0
        self.current_attack = 0
        
        self.base_durability = 0
        self.current_durability = 0