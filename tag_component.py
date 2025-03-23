from game_event_labels import GameEventLabel
from hearsay.entity_tag import EntityTag
from hearsay.components import Listener, Component
from hearsay.rules import Rule
from hearsay.out_var import OutVar

class TagComponent(Component):
    def __init__(self, tag_type:type, tag:EntityTag):
        self._tag_type = tag_type
        self._tag = tag
        super().__init__()

    @Listener(GameEventLabel.REQUEST_TAGS)
    def _on_request_tags(self, candidate_id:int, tags_by_type:dict[type, EntityTag]):
        if not self._includes_attached_id(candidate_id):
            return
        tags_by_type[self._tag_type] = self._tag

    @Listener(GameEventLabel.REQUEST_PASSES_RULE)
    def _on_request_passes_rule(self, candidate_id:list[int], rule:Rule, passes_rule:dict[int, bool]):
        if not self._includes_attached_id(candidate_id):
            return
        passes_rule[self._id] = rule.check_entity(self._id)
