import enum
import tomllib
from typing import Dict, Any, List, Optional, Generator, Tuple

import pokerkit
import schema
from pokerkit import (HandHistory,
                      HoleDealing,
                      Card,
                      BoardDealing,
                      CheckingOrCalling,
                      CompletionBettingOrRaisingTo,
                      Folding)

from anki_poker_master.model import ValidationError
from anki_poker_master.model.hand import Hand, Player, Street


class _GameState(enum.Enum):
    SETUP = enum.auto()
    END_SETUP = enum.auto()
    PREFLOP = enum.auto()
    END_PREFLOP = enum.auto()
    FLOP = enum.auto()
    END_FLOP = enum.auto()
    TURN = enum.auto()
    END_TURN = enum.auto()
    RIVER = enum.auto()
    END_RIVER = enum.auto()
    FINALIZE = enum.auto()
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
        self._current_street_had_a_bet = False
        player_count = hh.create_state().player_count
        for i in range(player_count):
            name = f'p{i + 1}'
            if hh.players:
                name = hh.players[i]
            is_dealer = (i == player_count - 1)
            self._hand.players.append(Player(name, is_dealer, False))

    def get_hand(self) -> Hand:
        state_handler_mapping = {
            _GameState.SETUP: self._state_setup,
            _GameState.END_SETUP: self._state_end_setup,
            _GameState.PREFLOP: self._state_preflop,
            _GameState.END_PREFLOP: self._state_end_preflop,
            _GameState.FLOP: self._state_flop,
            _GameState.END_FLOP: self._state_end_flop,
            _GameState.TURN: self._state_turn,
            _GameState.END_TURN: self._state_end_turn,
            _GameState.RIVER: self._state_river,
            _GameState.END_RIVER: self._state_end_river,
            _GameState.FINALIZE: lambda: True,
            _GameState.DONE: lambda: True,
        }

        advance = True
        while self._machine_state != _GameState.DONE:
            if advance:
                try:
                    self._pk_current_state, self._pk_current_operation = next(self._pk_operation_iterator)
                except StopIteration:
                    self._machine_state = _GameState.DONE
            advance = state_handler_mapping[self._machine_state]()
        return self._hand

    @staticmethod
    def _create_pk_operation_iterator(hh: pokerkit.HandHistory) -> (
            Generator)[Tuple[pokerkit.State, pokerkit.Operation], None, None]:
        index = 0
        for s in hh:
            while index < len(s.operations):
                yield s, s.operations[index]
                index += 1

    def _state_setup(self) -> bool:
        if isinstance(self._pk_current_operation, HoleDealing):
            self._nr_players_dealt += 1
            if self._nr_players_dealt == self._pk_current_state.player_count:
                self._machine_state = _GameState.END_SETUP
                return False
        return True

    def _state_end_setup(self) -> bool:
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
        return True

    def _state_preflop(self):
        return self._street_state_helper(0, _GameState.END_PREFLOP)

    def _state_end_preflop(self) -> bool:
        self._current_street_had_a_bet = False
        pot_amounts = list(self._pk_current_state.pot_amounts)
        if not pot_amounts:
            pot_amounts = [0]
        self._hand.streets.append(
            Street(
                "Flop",
                [repr(c[0]) for c in self._pk_current_state.board_cards],
                pot_amounts,
                self._pk_current_state.statuses.copy(),
                self._pk_current_state.stacks.copy(),
                0,
                [[] for _ in range(self._pk_current_state.player_count)],
            )
        )
        self._machine_state = _GameState.FLOP
        return True

    def _state_flop(self) -> bool:
        return self._street_state_helper(1, _GameState.END_FLOP)

    def _state_end_flop(self):
        self._current_street_had_a_bet = False
        pot_amounts = list(self._pk_current_state.pot_amounts)
        if not pot_amounts:
            pot_amounts = [0]
        self._hand.streets.append(
            Street(
                "Turn",
                [repr(c[0]) for c in self._pk_current_state.board_cards],
                pot_amounts,
                self._pk_current_state.statuses.copy(),
                self._pk_current_state.stacks.copy(),
                0,
                [[] for _ in range(self._pk_current_state.player_count)],
            )
        )
        self._machine_state = _GameState.TURN
        return True

    def _state_turn(self) -> bool:
        return self._street_state_helper(2, _GameState.END_TURN)

    def _state_end_turn(self) -> bool:
        self._current_street_had_a_bet = False
        pot_amounts = list(self._pk_current_state.pot_amounts)
        if not pot_amounts:
            pot_amounts = [0]
        self._hand.streets.append(
            Street(
                "River",
                [repr(c[0]) for c in self._pk_current_state.board_cards],
                pot_amounts,
                self._pk_current_state.statuses.copy(),
                self._pk_current_state.stacks.copy(),
                0,
                [[] for _ in range(self._pk_current_state.player_count)],
            )
        )
        self._machine_state = _GameState.RIVER
        return True

    def _state_river(self) -> bool:
        return self._street_state_helper(3, _GameState.END_RIVER)

    def _state_end_river(self) -> bool:
        self._current_street_had_a_bet = False
        self._machine_state = _GameState.FINALIZE
        return True

    def _street_state_helper(self, current_street_index: int, next_state: _GameState) -> bool:
        """
        Method to process a specific street i.e. preflop, flop, turn and river.
        """
        if isinstance(self._pk_current_operation, BoardDealing):
            self._machine_state = next_state
            return False
        elif isinstance(self._pk_current_operation, CheckingOrCalling):
            self._hand.streets[current_street_index].actions[self._pk_current_operation.player_index].append(
                "C" if self._current_street_had_a_bet else "X")
        elif isinstance(self._pk_current_operation, CompletionBettingOrRaisingTo):
            self._hand.streets[current_street_index].actions[self._pk_current_operation.player_index].append(
                f'{"R" if self._current_street_had_a_bet else "B"} {self._pk_current_operation.amount}')
            self._current_street_had_a_bet = True
        elif isinstance(self._pk_current_operation, Folding):
            self._hand.streets[current_street_index].actions[self._pk_current_operation.player_index].append("F")
        return True



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
