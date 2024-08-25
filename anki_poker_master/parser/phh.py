import tomllib
from typing import Dict, Any

from pokerkit import HandHistory, HoleDealing

from anki_poker_master.model import ValidationError
from anki_poker_master.model.hand import Hand, Player


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

    custom_fields = _get_custom_fields(content)
    # TODO validate these with a schema e.g. type and length

    state = hh.create_state()

    if '_apm_hero' in custom_fields:
        fail = False
        try:
            apm_hero = int(custom_fields['_apm_hero'])
            if not (0 < apm_hero <= state.player_count):
                fail = True
        except ValueError:
            fail = True
        if fail:
            raise ValidationError(f"'_apm_hero' must be a number between 1 and {state.player_count}")

    my_hand = Hand()
    for i in range(state.player_count):
        name = f'p{i + 1}'
        if hh.players:
            name = hh.players[i]
        is_dealer = (i == state.player_count - 1)
        my_hand.players.append(Player(name, is_dealer, False))

    operation_index = 0
    for state in hh:
        while operation_index < len(state.operations):
            operation = state.operations[operation_index]
            operation_index += 1
            if isinstance(operation, HoleDealing):
                True

    hole_cards_are_known = []
    for cards in state.hole_cards:
        hole_cards_are_known.append(all(not c.unknown_status for c in cards))
    if '_apm_hero' in custom_fields:
        if hole_cards_are_known[custom_fields['_apm_hero']-1]:
            my_hand.players[custom_fields['_apm_hero']-1].is_hero = True
        else:
            raise ValidationError("The hole cards of the hero must be known.")
    elif hole_cards_are_known.count(True) == 0:
        raise ValidationError("The hole cards of the hero must be known.")
    elif hole_cards_are_known.count(True) > 1:
        raise ValidationError("The hole cards of only one player must be known.")
    else:
        my_hand.players[hole_cards_are_known.index(True)].is_hero = True

    return my_hand


def _get_custom_fields(content: str) -> Dict[str, Any]:
    custom_fields = dict()
    raw_hh = tomllib.loads(content)
    for key, val in raw_hh.items():
        if key.startswith("_apm"):
            custom_fields[key] = val
    return custom_fields
