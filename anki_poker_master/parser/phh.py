import enum
import tomllib
from typing import Dict, Any, List, Optional, Generator, Tuple

import pokerkit
import schema
from pokerkit import HandHistory, HoleDealing, Card

from anki_poker_master.model import ValidationError
from anki_poker_master.model.hand import Hand, Player, Street


class _GameState(enum.Enum):
    SETUP = enum.auto()
    END_SETUP = enum.auto()
    PREFLOP = enum.auto()
    DONE = enum.auto()


class _StateMachine:
    _machine_state: _GameState
    _pk_operation_iterator: Generator[Tuple[pokerkit.State, pokerkit.Operation], None, None]
    _pk_current_state: pokerkit.State
    _pk_current_operation: pokerkit.Operation
    _nr_players_dealt: int
    _hand: Hand

    def __init__(self, hh: pokerkit.HandHistory, custom_fields: Dict[str, Any]):
        self._machine_state = _GameState.SETUP
        self._pk_operation_iterator = self._create_pk_operation_iterator(hh)
        self._nr_players_dealt = 0
        self._custom_fields = custom_fields
        self._hand = Hand()
        player_count = hh.create_state().player_count
        for i in range(player_count):
            name = f'p{i + 1}'
            if hh.players:
                name = hh.players[i]
            is_dealer = (i == player_count - 1)
            self._hand.players.append(Player(name, is_dealer, False))

    def get_hand(self) -> Hand:
        while self._machine_state != _GameState.DONE:
            # why do I need the current_state, only for player_count?
            try:
                self._pk_current_state, self._pk_current_operation = next(self._pk_operation_iterator)
            except StopIteration:
                self._machine_state = _GameState.DONE
            if self._machine_state == _GameState.SETUP:
                self._state_setup()
            elif self._machine_state == _GameState.END_SETUP:
                pass
            elif self._machine_state == _GameState.PREFLOP:
                pass
        return self._hand

    @staticmethod
    def _create_pk_operation_iterator(hh: pokerkit.HandHistory) -> (
            Generator)[Tuple[pokerkit.State, pokerkit.Operation], None, None]:
        index = 0
        for s in hh:
            while index < len(s.operations):
                yield s, s.operations[index]
                index += 1

    def _state_setup(self):
        if isinstance(self._pk_current_operation, HoleDealing):
            self._nr_players_dealt += 1
            if self._nr_players_dealt == self._pk_current_state.player_count:
                hero_index, self._hand.hero_cards = _get_hero(self._pk_current_state.hole_cards,
                                                              self._custom_fields.get("_apm_hero", None))
                self._hand.players[hero_index].is_hero = True
                blinds = sum(self._pk_current_state.blinds_or_straddles)
                pot_amounts = list(self._pk_current_state.pot_amounts)
                if not pot_amounts:
                    pot_amounts = [0]
                pot_amounts[0] += blinds
                self._hand.streets.append(
                    Street(
                        "Preflop",
                        [],
                        pot_amounts,
                        [True for _ in range(self._pk_current_state.player_count)],
                        self._pk_current_state.stacks.copy(),
                        2,
                        [[] for _ in range(self._pk_current_state.player_count)],
                    )
                )
                self._machine_state = _GameState.PREFLOP


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

    custom_fields = _get_and_validate_custom_fields(content, hh.create_state().player_count)
    state_machine = _StateMachine(hh, custom_fields)
    return state_machine.get_hand()


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
