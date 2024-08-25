import enum
import tomllib
from typing import Dict, Any, List, Optional

import schema
from pokerkit import HandHistory, HoleDealing, Card

from anki_poker_master.model import ValidationError
from anki_poker_master.model.hand import Hand, Player, Street


class _GameState(enum.Enum):
    SETUP = enum.auto()
    END_SETUP = enum.auto()
    PREFLOP = enum.auto()

def parse_phh(content: str) -> Hand:
    if not content:
        raise ValidationError("Invalid PHH (empty)")
    try:
        hh = HandHistory.loads(content)
    except Exception as e:
        if len(content) > 100:
            content_for_err = content[:100] + "\n..."
        else:
            content_for_err = content
        raise ValidationError(f'Error parsing PHH with content:\n{content_for_err}') from e

    if hh.variant != "NT":
        # TODO Validate whether other variants work with little additional effort, but for now focus on NLHE
        raise ValidationError(f"the variant '{hh.variant}' is not supported")

    pk_state = hh.create_state()

    custom_fields = _get_and_validate_custom_fields(content, pk_state.player_count)

    my_hand = Hand()
    for i in range(pk_state.player_count):
        name = f'p{i + 1}'
        if hh.players:
            name = hh.players[i]
        is_dealer = (i == pk_state.player_count - 1)
        my_hand.players.append(Player(name, is_dealer, False))

    state = _GameState.SETUP
    dealing_counter = 0
    operation_index = 0
    for pk_state in hh:
        while operation_index < len(pk_state.operations):
            operation = pk_state.operations[operation_index]
            operation_index += 1
            if state is _GameState.SETUP:
                if isinstance(operation, HoleDealing):
                    dealing_counter += 1
                    if dealing_counter == pk_state.player_count:
                        state = _GameState.END_SETUP
            if state is _GameState.END_SETUP:
                hero_index, my_hand.hero_cards = _get_hero(pk_state.hole_cards, custom_fields.get("_apm_hero", None))
                my_hand.players[hero_index].is_hero = True
                blinds = sum(pk_state.blinds_or_straddles)
                pot_amounts = list(pk_state.pot_amounts)
                if not pot_amounts:
                    pot_amounts = [0]
                pot_amounts[0] += blinds
                my_hand.streets.append(
                    Street(
                        "Preflop",
                        [],
                        pot_amounts,
                        [True for _ in range(pk_state.player_count)],
                        pk_state.stacks.copy(),
                        2,
                        [[] for _ in range(pk_state.player_count)],
                    )
                )
                state = _GameState.PREFLOP
                continue

    return my_hand


def _get_and_validate_custom_fields(content: str, player_count: int) -> Dict[str, Any]:
    custom_fields = dict()
    raw_hh = tomllib.loads(content)
    for key, val in raw_hh.items():
        if key.startswith("_apm"):
            custom_fields[key] = val

    custom_fields_schema = schema.Schema(
        {
            schema.Optional("_apm_hero"): schema.And(
                int,
                schema.Schema(lambda n: 0 < n <= player_count, error=f"must be between 1 and {player_count}"),
            ),
            schema.Optional("_apm_source"): str,
            schema.Optional("_apm_notes"): str,
            schema.Optional("_apm_context"): str,
            schema.Optional("_apm_answers"): [str],
        }
    )

    try:
        return custom_fields_schema.validate(custom_fields)
    except schema.SchemaError as e:
        raise ValidationError(f'Error validating user-defined "_apm" fields') from e


def _get_hero(hole_cards: List[List[Card]], apm_hero: Optional[int]) -> (int, List[str]):
    hole_cards_are_known = []
    for cards in hole_cards:
        hole_cards_are_known.append(all(not c.unknown_status for c in cards))
    if apm_hero is not None:
        index = apm_hero - 1
        if hole_cards_are_known[index]:
            return index, [repr(c) for c in hole_cards[index]]
        else:
            raise ValidationError("The hole cards of the hero must be known.")
    elif hole_cards_are_known.count(True) == 0:
        raise ValidationError("The hole cards of the hero must be known.")
    elif hole_cards_are_known.count(True) > 1:
        raise ValidationError("The hole cards of only one player must be known.")
    else:
        index = hole_cards_are_known.index(True)
        return index, [repr(c) for c in hole_cards[index]]
