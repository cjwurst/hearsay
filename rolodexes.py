from typing import Generic, TypeVar
from enum import Enum

from hearsay.components import Component, Listener
from hearsay.out_var import OutVar

from game_event_labels import GameEventLabel

class EntityRolodex(Enum):
    pass

RT = TypeVar('RT', bound = EntityRolodex)
"""A component which allows its entity to keep track of the ids of other entities."""
class RolodexComponent(Component, Generic[RT]):
    def __init__(self, initial_rolodex):
        self._rolodex = initial_rolodex
        super().__init__()

    @Listener(GameEventLabel.REQUEST_ROLODEX_LOOKUP, 0)
    def _on_request_rolodex_lookup(self, rolodex_holder_id:int, enumerated_name:Enum, request:OutVar[int]):
        if not self._includes_attached_id(rolodex_holder_id):
            return
        request.result = self._rolodex[enumerated_name]

PT = TypeVar('PT', bound = EntityRolodex)
"""A component which overrides rolodex entries on its entity."""
class RolodexProxyComponent(Generic[PT], RolodexComponent[PT]):
    def __init__(self, initial_rolodex):
        self._rolodex = initial_rolodex
        super().__init__()

    @Listener(GameEventLabel.REQUEST_ROLODEX_LOOKUP, -1)
    def _on_request_rolodex_lookup(self, rolodex_holder_id:int, enumerated_name:Enum, request:OutVar[int]):
        super()._on_request_rolodex_lookup(self, rolodex_holder_id, enumerated_name, request)
