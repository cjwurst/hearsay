from hearsay.components import Component, Listener
from hearsay.rules import Rule

from game_event_labels import GameEventLabel

class RuleChecker(Component):
    @Listener(GameEventLabel.REQUEST_PASSES_RULE)
    def _on_request_passes_rule(self, candidate_ids:list[int], rule:Rule, passes_rule_by_id:dict[int, bool]):
        if self._includes_attached_id(candidate_ids):
            passes_rule_by_id[self.id] = rule.check_entity(self.id)
