from __future__ import annotations

from numpy import iterable
from hearsay.invertibles import Invertible, InvertibleStack
import hearsay.debug as debug
from game_event_labels import GameEventLabel



"""The event loop."""
class EventDirector:
    def __init__(self):
        self._stack = InvertibleStack()
        self._game_events = {}
        for label in GameEventLabel:
            self._game_events[label.value] = _GameEvent(label)
    
    def subscribe(self, event_label, priority:int, response:callable):
        """Subscribe to a game event. Return an unsubscribe function. Components are responsible for subscribing to and unsubscribing from events."""
        return self._game_events[event_label.value].subscribe(response, priority)

    def invoke_game_event(self, event_label:GameEventLabel, *args):
        """Invoke a game event."""
        debug.label_hierarchy.append(event_label)
        try:
            invertibles = self._game_events[event_label.value].invoke(*args)
        except Exception:
            raise
        for invertible in invertibles:
            self._stack.push(invertible)
        debug.label_hierarchy.pop()

    #def push_to_stack(self, invertible: Invertible):
    #    self._stack.push(invertible)

class _GameEvent:
    def __init__(self, label:GameEventLabel):
        self._event_label = label
        self._subscribers = []
        self._priorities = {}

    def subscribe(self, closure:callable, priority:int = 0):
        pass
        self._priorities[closure] = priority
        self._subscribers.append(closure)
        def unsub():
            self._unsubscribe(closure)
        return unsub

    def _unsubscribe(self, closure:callable):
        self._subscribers.remove(closure)
        del self._priorities[closure]

    def _sort_subscribers(self):
        self._subscribers.sort(reverse = True, key = lambda s : self._priorities[s])

    #TODO: Only sort when necessary
    def invoke(self, *args) -> list[Invertible]:
        invertibles = []
        self._sort_subscribers()
        subs = self._subscribers.copy()             # This prevents state changes within subscribers from changing the list during invocation
        for subscriber in subs:
            try:
                result = subscriber(*args)
                if result != None:
                    if iterable(result):
                        invertibles += result
                    else:
                        invertibles.append(result)
            except:
                raise
        return invertibles
