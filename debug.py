from dataclasses import dataclass
from typing import Type

from game_event_labels import GameEventLabel

# To log all event responsed subscribed to a given label, type "debug_label(GameEventLabel.<LABEL_NAME>)" at a breakpoint.
# To view the current label hierarcy, type "label_hierarchy".

@dataclass
class _DebugString:
    owner: Type
    priority: int
    response_name: str

    def __str__(self) -> str:
        return f"{self.owner.__name__ : <30}.{self.response_name : <30}{str(self.priority) : >8}"

_event_responses_by_label: dict[GameEventLabel, list[_DebugString]] = {}            # Populated by the Listener class via push_response

def push_response(label:GameEventLabel, owner, priority:int, response_name:str):
    if label not in _event_responses_by_label.keys():
        _event_responses_by_label[label] = []
    _event_responses_by_label[label].append(_DebugString(owner, priority, response_name))

def debug_label(label:GameEventLabel) -> str:
    result = f"\n{'Component' : <30}{'Response Name' : <30}{'Priority' : >8}\n\n"
    string_list = _event_responses_by_label[label].sort(key = lambda s: s.priority, reverse = True)
    for s in _event_responses_by_label[label]:
        result += str(s) + '\n'
    print(result)
    return result

label_hierarchy:list[GameEventLabel] = []