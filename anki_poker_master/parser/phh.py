import enum
import tomllib
from typing import Dict, Any, List, Optional, Generator, Tuple, Callable

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


class _ParserState(enum.Enum):
    """
    Represents the different states the parser can be in while it's parsing the hand history.
    """
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


class _Parser:
    """
    Parse and convert a pokerkit.HandHistory into a model.Hand . Strictly speaking 'parsing'
    might be the wrong term since pokerkit.HandHistory is already an object that was
    produced by parsing a .phh file.
    """
    _parser_state: _ParserState
    _pk_operation_iterator: Generator[Tuple[pokerkit.State, pokerkit.Operation], None, None]
    _pk_current_state: pokerkit.State
    _pk_current_operation: pokerkit.Operation
    _nr_players_dealt: int
    _hand: Hand

    def __init__(self, hh: pokerkit.HandHistory, custom_fields: Dict[str, Any]):
        """
        :param hh: valid pokerkit.HandHistory object
        :param custom_fields: valid custom (user-defined) fields extracted from the
            .phh file (e.g. _apm_source).
        """
        self._parser_state = _ParserState.SETUP
        self._pk_operation_iterator = self._create_pk_operation_iterator(hh)
        self._nr_players_dealt = 0
        self._custom_fields = custom_fields
        self._hand = Hand()
        if custom_fields.get("_apm_notes", None):
            self._hand.notes = custom_fields["_apm_notes"]
        if custom_fields.get("_apm_source", None):
            self._hand.source = custom_fields["_apm_source"]
        if custom_fields.get("_apm_context", None):
            self._hand.context = custom_fields["_apm_context"]
        self._current_street_had_a_bet = False
        player_count = hh.create_state().player_count
        for i in range(player_count):
            name = f'p{i + 1}'
            if hh.players:
                name = hh.players[i]
            is_dealer = (i == player_count - 1)
            self._hand.players.append(Player(name, is_dealer, False))

    def get_hand(self) -> Hand:
        """
        Does all the heavy lifting and returns a Hand object.

        :return: A Hand object.
        """

        # Map states to handler functions. The handler functions return True if the next pokerkit
        # operation should be processed, False if the same operation should be processed again
        # (e.g. because we only recognize the current state is done thanks to the first operation
        # of the next state).
        state_handler_mapping: Dict[_ParserState, Callable[[], bool]] = {
            _ParserState.SETUP: self._state_handler_setup,
            _ParserState.END_SETUP: self._state_handler_end_setup,
            _ParserState.PREFLOP: lambda: self._street_state_helper(0, _ParserState.END_PREFLOP),
            _ParserState.END_PREFLOP: lambda: self._street_end_state_helper("Flop", _ParserState.FLOP),
            _ParserState.FLOP: lambda: self._street_state_helper(1, _ParserState.END_FLOP),
            _ParserState.END_FLOP: lambda: self._street_end_state_helper("Turn", _ParserState.TURN),
            _ParserState.TURN: lambda: self._street_state_helper(2, _ParserState.END_TURN),
            _ParserState.END_TURN: lambda: self._street_end_state_helper("River", _ParserState.RIVER),
            _ParserState.RIVER: lambda: self._street_state_helper(3, _ParserState.FINALIZE),
            _ParserState.FINALIZE: lambda: True,  # Allow pokerkit to run through until the end
            _ParserState.DONE: lambda: True,
        }

        advance_pk_operation = True
        while self._parser_state != _ParserState.DONE:
            if advance_pk_operation:
                try:
                    self._pk_current_state, self._pk_current_operation = next(self._pk_operation_iterator)
                except StopIteration:
                    self._parser_state = _ParserState.DONE
            advance_pk_operation = state_handler_mapping[self._parser_state]()
        return self._hand

    @staticmethod
    def _create_pk_operation_iterator(hh: pokerkit.HandHistory) -> (
            Generator)[Tuple[pokerkit.State, pokerkit.Operation], None, None]:
        """
        Helper function to create a generator to iterate over pokerkit states and operations.
        """
        index = 0
        for s in hh:
            while index < len(s.operations):
                yield s, s.operations[index]
                index += 1

    def _state_handler_setup(self) -> bool:
        """
        Handle the initial operations that we are not interested in. We know the state is done
        once all cards have been dealt.
        """
        if isinstance(self._pk_current_operation, HoleDealing):
            self._nr_players_dealt += 1
            if self._nr_players_dealt == self._pk_current_state.player_count:
                self._parser_state = _ParserState.END_SETUP
                return False
        return True

    def _state_handler_end_setup(self) -> bool:
        """
        Initialize the pots, figure out which player is the hero and then transition to preflop.
        """
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
        self._parser_state = _ParserState.PREFLOP
        return True

    def _street_state_helper(self, current_street_index: int, next_state: _ParserState) -> bool:
        """
        Helper method to do the processing of the streets (preflop, flop, ...), used by the
        relevant _state_handlers .

        :param current_street_index: index of the street being processed in self._hand.streets .
        :param next_state: state to set once the board is dealt (i.e. the current street ends).
        :returns: boolean whether processing should continue with the next pokerkit operation
            (or stay on the current one).
        """
        if isinstance(self._pk_current_operation, BoardDealing):
            self._parser_state = next_state
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

    def _street_end_state_helper(self, next_street_name: str, next_state: _ParserState) -> bool:
        """
        Helper method to do the processing of the end of streets (end_preflop, end_flop, ...), used by the
        relevant _state_handlers .
        """
        self._current_street_had_a_bet = False
        pot_amounts = list(self._pk_current_state.pot_amounts)
        if not pot_amounts:
            pot_amounts = [0]
        self._hand.streets.append(
            Street(
                next_street_name,
                [repr(c[0]) for c in self._pk_current_state.board_cards],
                pot_amounts,
                self._pk_current_state.statuses.copy(),
                self._pk_current_state.stacks.copy(),
                0,
                [[] for _ in range(self._pk_current_state.player_count)],
            )
        )
        self._parser_state = next_state
        return True


def parse(content: str) -> Hand:
    """
    Parse the content of a .phh (poker hand history) file.

    :param content: content of the .phh (poker hand history) file.
    :returns: the parsed hand.
    """
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
    parser = _Parser(hh, custom_fields)
    return parser.get_hand()


def _get_and_validate_custom_fields(content: str, player_count: int) -> Dict[str, Any]:
    """
    The .phh file may contain custom fields (called user-defined fields in the specification). We
    are only interested in the ones starting with '_apm_' so we filter and validate them.

    :param content: content of the .phh (poker hand history) file.
    :param player_count: number of players in the poker hand history.
    :returns: the parsed and validated custom fields.
    """
    custom_fields = dict()
    raw_hh = tomllib.loads(content)
    for key, val in raw_hh.items():
        if key.startswith("_apm_"):
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
    """
    Decide who the hero (player from whose perspective we are "watching" the hand) is.
    The pocket cards of the hero must be known and specified at the beginning of the hand history.
    If this is true for multiple players, the hero player must be specified with the
    "_apm_hero" custom value.
    "_apm_hero" takes precedence so if that player's pocket cards are unknown this would lead to
    an error even if another player's pocket cards are known.

    :param hole_cards: The hole or pocket cards per player
    :param apm_hero: The player who should be the hero according to the _apm_hero custom field.
        It starts at 1 because in the .phh file the players are numbered as p1, p2, ..., pN.
        It will be None if no custom value was set.
    :returns: The index (starting at 0) of the hero player and their pocket cards.
    """
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
