from game_event_labels import GameEventLabel
from hearsay.components import Listener, Component
from hearsay.out_var import OutVar

class DebugNameComponent(Component):
    def __init__(self, name:str):
        self._name = name
        super().__init__()

    @Listener(GameEventLabel.REQUEST_DEBUG_NAME)
    def _on_request_tags(self, candidate_id:int, name_request:OutVar[str]):
        if not self._includes_attached_id(candidate_id):
            return
        name_request.result = self._name