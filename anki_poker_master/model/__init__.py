from typing import Dict

import schema
from poker import Range

from anki_poker_master.helper import str_to_css_class


class ValidationError(ValueError):
    def __init__(self, message):
        super().__init__(message)

    def humanize_error(self) -> str:
        err_msg = f"{self.args[0]}"
        if self.__cause__ and type(self.__cause__) == schema.SchemaError:
            err_msg += ": " + self.__cause__.code
        return err_msg


class PreflopScenario:
    def __init__(
        self,
        ranges: Dict[str, Range],
        position: str,
        scenario: str,
        game: str,
        range_colors: Dict = None,
        notes: str = None,
        source: str = None,
    ):
        self.ranges = ranges.copy()
        if "fold" not in [r.lower() for r in self.ranges]:
            # Make the fold range explicit if it's missing
            all_hands = Range("XX").hands
            fold_hands = set(all_hands)
            for action in self.ranges:
                fold_hands -= set(self.ranges[action].hands)
            fold_range = Range.from_objects(fold_hands)
            if len(fold_range) > 0:
                self.ranges["Fold"] = fold_range
        self.position = position
        self.scenario = scenario
        self.game = game
        self.extra_range_colors = {}
        if range_colors is not None:
            for color_k, color_v in range_colors.items():
                self.extra_range_colors[str_to_css_class(color_k)] = color_v
        self.notes = notes
        self.source = source
