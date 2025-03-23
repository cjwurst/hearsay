from asyncio import events
import warnings

from abc import ABC
from game_event_labels import GameEventLabel

from hearsay.event_director import EventDirector
from hearsay.entity_tag import EntityTag
from hearsay.class_property import ReadonlyStaticProperty

"""A predicate that takes an entity id as an input.
Rules are used via REQUEST_PASSES_RULE events as a shortcut to test predicates without retrieving data directly."""
class Rule:
    def __init__(self, predicate:callable):
        self._nested_check_entity = predicate
        self.debug_string = None

    def __str__(self) -> str:
        if self.debug_string == None:
            return super().__str__()
        return self.debug_string

    # Override this method to check a rule at only the shallowest level of a rule composition.          #TODO: Needs testing
    def check_entity(self, id:int) -> bool:
        return self._nested_check_entity(id)

    @ReadonlyStaticProperty
    def contradiction():
        return Rule(lambda _: False)

    @ReadonlyStaticProperty
    def tautalogy():
        return Rule(lambda _: True)

    @staticmethod
    def has_tags(event_director:EventDirector, tag_type:type, *desired_tags:EntityTag):         #TODO: is it necessary to pass tag_type here?
        def predicate(event_director:EventDirector, id:int):
            tags = {}
            event_director.invoke_game_event(GameEventLabel.REQUEST_TAGS, id, tags)
            try:
                for tag in desired_tags:
                    if tag not in tags[tag_type]:
                        return False
            except KeyError:
                warnings.warn('Entity with id {id} did not respond to {GameEventLabel.REQUEST_TAGS}')
                return False
            return True
        rule = Rule(lambda id: predicate(event_director, id))
        rule.debug_string = f"Has tags: {desired_tags}"
        return rule

    @staticmethod
    def has_any_of_tags(event_director:EventDirector, tag_type:type, *desired_tags:EntityTag):
        def predicate(event_director:EventDirector, id:int):
            tags = {}
            event_director.invoke_game_event(GameEventLabel.REQUEST_TAGS, id, tags)
            try:
                for tag in desired_tags:
                    if tag in tags[tag_type]:
                        return True
            except KeyError:
                warnings.warn('Entity with id {id} did not respond to {GameEventLabel.REQUEST_TAGS}')
            return False
        rule = Rule(lambda id: predicate(event_director, id))
        rule.debug_string = f"Has any of tags: {desired_tags}"
        return rule

    @staticmethod
    def lacks_tags(event_director:EventDirector, tag_type:type, *undesired_tags:EntityTag):
        def predicate(event_director:EventDirector, id:int):
            tags = {}
            event_director.invoke_game_event(GameEventLabel.REQUEST_TAGS, id, tags)
            try:
                for tag in undesired_tags:
                    if tag in tags[tag_type]:
                        return False
            except KeyError:
                warnings.warn('Entity with id {id} did not respond to {GameEventLabel.REQUEST_TAGS}')
            return True
        rule = Rule(lambda id: predicate(event_director, id))
        rule.debug_string = f"Doesn't have tags: {undesired_tags}"
        return rule

    @staticmethod
    def compose(*subrules:'Rule'):
        def predicate(id):
            for rule in subrules:
                if rule._nested_check_entity(id) is False:
                    return False
            return True
        debug_string = 'Passes rules:\n'
        for rule in subrules:
            debug_string += '     ' + str(rule) + '\n'
        rule = Rule(predicate)
        rule.debug_string = debug_string
        return rule

    @staticmethod
    def negate(rule:'Rule'):
        def predicate(id):
            return rule.check_entity(id) is False
        return Rule(predicate)
