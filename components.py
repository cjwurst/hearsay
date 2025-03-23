from abc import ABC

from hearsay.debug import push_response, debug_label, label_hierarchy
from hearsay.event_director import EventDirector
from hearsay.invertibles import Invertible
from hearsay.class_property import ReadonlyClassProperty

from game_event_labels import GameEventLabel
from typing import TypeVar, Generic
from component_states import ComponentState
from hearsay.out_var import OutVar

"""An object which defines a particular behavior for a GameObject. 
Child classes override listener tags and implement a function called 'on_{event_label}' for each tag. Listeners are then made via reflection in this constructor.

A component must make sure that the self ID is consistent and also that the predicate is valid.
When making a call to event_director, you do not include the leading self or the trailing invertibles and game_predicate, they are handled for you.

Object state is only read in 'REQUEST_...' game events, and state is only written through invertibles in 'TRY_...' game events."""
class Component(ABC):
    #TODO:This is pretty awkward...
    _listeners_by_class = {}

    @property
    def debug_name(self):
        name_request = OutVar[str]()
        self._event_director.invoke_game_event(GameEventLabel.REQUEST_DEBUG_NAME, self.id, name_request)
        if name_request.has_been_set:
            return name_request.result
        return 'Untitled'

    @property
    def id(self):
        return self._id

    @classmethod
    def append_listener(cls, listener:'Listener'):
        cls._listeners.append(listener)

    # This mess ensures that listeners are inherited properly.
    @ReadonlyClassProperty
    def _listeners(cls) -> list:
        if cls not in cls._listeners_by_class.keys():
            cls._listeners_by_class[cls] = []
            for parent in cls.__mro__:
                if parent == cls:
                    continue
                if parent in cls._listeners_by_class.keys():
                    cls._listeners_by_class[cls] = cls._listeners_by_class[parent].copy()
                    break
        return cls._listeners_by_class[cls]

    def __init__(self):
        self._id = None

    def attach(self, event_director:EventDirector, id:int):
        self._id = id
        self._event_director = event_director
        self._unsubscribes = _UnsubscribeWrapper()
        self._subscribe()

    def detach(self):
        self._id = None
        for unsubscribe in self._unsubscribes:
            unsubscribe()

    def _subscribe(self):
        for listener in self._listeners:
            self._unsubscribes.append(listener.event_label, listener.subscribe(self, self._event_director))

    """Return True if the id(s) passed permit the game object this component is attached to."""
    def _includes_attached_id(self, id:int or list[int]) -> bool:
        if type(id) == list:
            return self._id in id
        return self._id == id or id == None

    def _try_rolodex_lookup(self, rolodex_entry, rolodex_holder_id = None):
        if rolodex_holder_id == None:
            rolodex_holder_id = self._id
        result = OutVar[int]()
        self._event_director.invoke_game_event(GameEventLabel.REQUEST_ROLODEX_LOOKUP, rolodex_holder_id, rolodex_entry, result)
        return result.result

"""An object instantiated as a decorator which subscribes the decorated function to the event director."""
class Listener:
    def __init__(self, label:GameEventLabel, priority:int = 0, inclusive_restrictions = None, exclusive_restrictions = None):
        self.event_label = label
        self.priority = priority
        self.inclusive_restrictions = inclusive_restrictions
        self.exclusive_restrictions = exclusive_restrictions

    def __set_name__(self, owner:Component, name:str):
        owner.append_listener(self)
        setattr(owner, name, self.response)
        push_response(self.event_label, owner, self.priority, name)

    def __call__(self, response:callable):
        self.response_name = response.__name__
        self.response = response
        return self

    def subscribe(self, subscriber:Component, event_director:EventDirector):
        # TODO: This is a problem with listener inheritance that needs to be addressed!
        return event_director.subscribe(self.event_label, self.priority, getattr(subscriber, self.response_name))

FT = TypeVar('FT', bound = ComponentState)
class GenericComponent(Component, ABC, Generic[FT]):
    #TODO:This is pretty awkward...
    _state_restrictions_by_class = {}

    # This mess ensures that listeners are inherited properly.
    @ReadonlyClassProperty
    def _state_restrictions(cls) -> list:
        if cls not in cls._state_restrictions_by_class.keys():
            cls._state_restrictions_by_class[cls] = []
            for parent in cls.__mro__:
                if parent == cls:
                    continue
                if parent in cls._state_restrictions_by_class.keys():
                    cls._state_restrictions_by_class[cls] = cls._state_restrictions_by_class[parent].copy()
                    break
        return cls._state_restrictions_by_class[cls]

    def __init__(self, state_type):
        self._component_state = None
        self._state_type = state_type
        super().__init__()

    # TODO: change state to the game object's state
    def attach(self, event_director:EventDirector, id:int):
        super().attach(event_director, id)

    def detach(self):
        self._component_state = None
        super().detach()

    @classmethod
    def append_listener(cls, listener:'Listener'):
        cls._state_restrictions.append((listener.inclusive_restrictions, listener.exclusive_restrictions))
        super().append_listener(listener) 

    def _subscribe(self):
        #self._unsubscribes.append(GameEventLabel.TRY_CHANGE_STATE, self._event_director.subscribe(GameEventLabel.TRY_CHANGE_STATE, 0, self._change_state))
        for listener in [self._listeners[i] for i in GenericComponent._get_matching_flags(self._component_state, self._state_restrictions)]:
            self._unsubscribes.append(listener.event_label, listener.subscribe(self, self._event_director))

    @Listener(GameEventLabel.TRY_CHANGE_STATE)
    def _change_state(self, id:int, state:ComponentState):
        if (type(state) != self._state_type) or not self._includes_attached_id(id):
            return
        return self._get_change_state_invertible(state)

    def _get_change_state_invertible(self, state) -> Invertible:
        old_state = self._component_state

        def sub():
            for unsubscribe in self._unsubscribes:
                unsubscribe()
            self._subscribe()

        def do():
            self._component_state = state
            sub()

        def undo():
            self._component_state = old_state
            sub()

        return Invertible(do, undo)

    """Return the indices of the restrictions which match the candidate as a list."""
    @staticmethod
    def _get_matching_flags(candidate:FT, restrictions:list[(FT, FT)]) -> list[int]:
        matching_indices = []
        for i in range(0, len(restrictions)):
            inclusive, exclusive = restrictions[i]
            if candidate == None:
                if inclusive:
                    continue
            else:
                if inclusive != None and (~candidate & inclusive):
                    continue
                if exclusive != None and (candidate & exclusive):
                    continue
            matching_indices.append(i)
        return matching_indices

# Protect unsubscribe closures and enforce that they are removed from self._unsubscribes when called.
class _UnsubscribeWrapper():
    def __init__(self):
        self._unsubscribes = []

    def __iter__(self):
        def call_and_remove(label:GameEventLabel, closure:callable):
            closure()
            self._unsubscribes.remove((label, closure))
        result = iter([(lambda f = f: call_and_remove(*f)) for f in self._unsubscribes])
        return result

    def append(self, label:GameEventLabel, closure:callable):
        self._unsubscribes.append((label, closure))

__all__ = ['Component', 'GenericComponent', 'Listener', 'debug_label', 'label_hierarchy']
