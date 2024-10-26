import enum
import tomllib
from typing import Dict, Any, List, Optional, Generator, Tuple, Callable

import pokerkit
import schema
from pokerkit import (
    HandHistory,
    HoleDealing,
    Card,
    BoardDealing,
    CheckingOrCalling,
    CompletionBettingOrRaisingTo,
    Folding,
)

from anki_poker_master.helper import format_n
from anki_poker_master.model import ValidationError
from anki_poker_master.model.hand import (
    Hand,
    Player,
    Street,
    Question,
    Action,
    CallAction,
    CheckAction,
    BetAction,
    RaiseAction,
    FoldAction,
)


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
    _pk_operation_iterator: Generator[
        Tuple[pokerkit.State, pokerkit.Operation], None, None
    ]
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
        if custom_fields.get("_apm_answers", None):
            self._hand.answers = custom_fields["_apm_answers"]
        player_count = hh.create_state().player_count
        for i in range(player_count):
            name = f"p{i + 1}"
            if hh.players:
                name = hh.players[i]
            is_dealer = i == player_count - 1
            self._hand.players.append(Player(name, is_dealer, False))
        if hh.variant == "NT":
            self._hand.title = "NLHE"
        elif hh.variant == "FT":
            self._hand.title = "LHE"
        else:
            self._hand.title = hh.variant

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
            _ParserState.PREFLOP: lambda: self._street_state_helper(
                0, _ParserState.END_PREFLOP
            ),
            _ParserState.END_PREFLOP: lambda: self._street_end_state_helper(
                "Flop", _ParserState.FLOP
            ),
            _ParserState.FLOP: lambda: self._street_state_helper(
                1, _ParserState.END_FLOP
            ),
            _ParserState.END_FLOP: lambda: self._street_end_state_helper(
                "Turn", _ParserState.TURN
            ),
            _ParserState.TURN: lambda: self._street_state_helper(
                2, _ParserState.END_TURN
            ),
            _ParserState.END_TURN: lambda: self._street_end_state_helper(
                "River", _ParserState.RIVER
            ),
            _ParserState.RIVER: lambda: self._street_state_helper(
                3, _ParserState.FINALIZE
            ),
            _ParserState.FINALIZE: lambda: True,  # Allow pokerkit to run through until the end
            _ParserState.DONE: self._state_handler_done,
        }

        advance_pk_operation = True
        while self._parser_state != _ParserState.DONE:
            if advance_pk_operation:
                try:
                    self._pk_current_state, self._pk_current_operation = next(
                        self._pk_operation_iterator
                    )
                except StopIteration:
                    self._parser_state = _ParserState.DONE
            advance_pk_operation = state_handler_mapping[self._parser_state]()
        return self._hand

    @staticmethod
    def _create_pk_operation_iterator(
        hh: pokerkit.HandHistory,
    ) -> (Generator)[Tuple[pokerkit.State, pokerkit.Operation], None, None]:
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
        hero_index, self._hand.hero_cards = _get_hero(
            self._pk_current_state.hole_cards,
            self._custom_fields.get("_apm_hero", None),
        )
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
        self._hand.title += " " + "/".join(
            format_n(b) for b in self._pk_current_state.blinds_or_straddles if b
        )
        if any(self._pk_current_state.antes):
            second_ante = self._pk_current_state.antes[1]
            if all(a == second_ante for a in self._pk_current_state.antes):
                self._hand.title += f" (ante {format_n(second_ante)})"
            else:
                # The ante is collected once per round from the BB
                self._hand.title += (
                    f" (ante {format_n(second_ante // len(self._hand.players))})"
                )
        self._parser_state = _ParserState.PREFLOP
        return True

    def _street_state_helper(
        self, current_street_index: int, next_state: _ParserState
    ) -> bool:
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
        if type(self._pk_current_operation) not in (
            CheckingOrCalling,
            CompletionBettingOrRaisingTo,
            Folding,
        ):
            # Skip the cases we are not interested in
            return True

        # Given that the actions are sorted by the order in which players act in a certain street
        # we need to calculate which row to use.
        player_i_for_action_table = (
            self._pk_current_operation.player_index
            - self._hand.streets[current_street_index].first_player_actions
        ) % self._pk_current_state.player_count
        commentary = self._pk_current_operation.commentary
        if commentary:
            commentary = commentary.strip()
        action: Action = Action()
        if isinstance(self._pk_current_operation, CheckingOrCalling):
            is_all_in = (
                self._pk_current_state.stacks[self._pk_current_operation.player_index]
                == 0
            )
            if self._pk_current_operation.amount > 0:
                action = CallAction(is_all_in)
            else:
                action = CheckAction()
        elif isinstance(self._pk_current_operation, CompletionBettingOrRaisingTo):
            is_bet = all(
                bet == 0 or i == self._pk_current_operation.player_index
                for i, bet in enumerate(self._pk_current_state.bets)
            )
            is_all_in = (
                self._pk_current_state.stacks[self._pk_current_operation.player_index]
                == 0
            )
            if is_bet:
                action = BetAction(self._pk_current_operation.amount, is_all_in)
            else:
                action = RaiseAction(self._pk_current_operation.amount, is_all_in)
        elif isinstance(self._pk_current_operation, Folding):
            action = FoldAction()
        if commentary and commentary.lower().startswith("apm study"):
            # The commentary marks which spot are a question (i.e. we want to study) and they may
            # also provide the answer (what comes after the colon). If the spot itself does not
            # provide an answer, then the answer is expected to be contained in the _apm_answers
            # custom field.
            answer: str = str(action)
            if commentary.lower().startswith("apm study:"):
                answer = commentary[len("apm study:") :].strip()
            else:
                # Choose the correct answer from _apm_answers
                number_previous_questions = 0
                for i in range(len(self._hand.streets)):
                    if i <= current_street_index:
                        number_previous_questions += len(
                            self._hand.streets[i].questions
                        )
                if (
                    number_previous_questions < len(self._hand.answers)
                    and self._hand.answers[number_previous_questions]
                ):
                    answer = self._hand.answers[number_previous_questions]
            next_action_i = len(
                self._hand.streets[current_street_index].actions[
                    player_i_for_action_table
                ]
            )
            self._hand.streets[current_street_index].questions.append(
                Question(
                    "What do you do?",
                    answer,
                    (player_i_for_action_table, next_action_i),
                )
            )
        elif self._hand.players[self._pk_current_operation.player_index].is_hero:
            # Collect the default questions for any action performed by the hero since we can't
            # know until the very end whether any "apm study" commentary exists. The default
            # questions would then be the fallback.
            answer: str = str(action)
            number_previous_questions = 0
            for i in range(len(self._hand.streets)):
                if i <= current_street_index:
                    number_previous_questions += len(
                        self._hand.streets[i].default_questions
                    )
            if (
                number_previous_questions < len(self._hand.answers)
                and self._hand.answers[number_previous_questions]
            ):
                answer = self._hand.answers[number_previous_questions]
            next_action_i = len(
                self._hand.streets[current_street_index].actions[
                    player_i_for_action_table
                ]
            )
            self._hand.streets[current_street_index].default_questions.append(
                Question(
                    "What do you do?",
                    answer,
                    (player_i_for_action_table, next_action_i),
                )
            )
        self._hand.streets[current_street_index].actions[
            player_i_for_action_table
        ].append(action)  # action should be a type to make it easier to style it later
        return True

    def _street_end_state_helper(
        self, next_street_name: str, next_state: _ParserState
    ) -> bool:
        """
        Helper method to do the processing of the end of streets (end_preflop, end_flop, ...), used by the
        relevant _state_handlers .
        """
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

    def _state_handler_done(self) -> bool:
        """
        Things to do once the entire .phh file has been parsed.
        """
        # Validate that the number of answers in _apm_answers matches the number of questions.
        # This can't be done without parsing all the actions, so it's easiest to do it at the end.
        # If necessary, replace the questions with the default questions.
        number_questions = sum(len(s.questions) for s in self._hand.streets)
        if number_questions == 0:
            number_questions = sum(len(s.default_questions) for s in self._hand.streets)
            for s in self._hand.streets:
                s.questions = s.default_questions
        for s in self._hand.streets:
            s.default_questions = []
        if self._hand.answers and len(self._hand.answers) != number_questions:
            raise ValidationError(
                f"_apm_answers contains {len(self._hand.answers)} answers "
                f"but {number_questions} questions are asked"
            )
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
        raise ValidationError(
            f"Error parsing PHH with content:\n{content_for_err}"
        ) from e

    if hh.variant not in ("NT", "FT"):
        # TODO Validate whether other variants work with little additional effort, but for now focus on NLHE
        raise ValidationError(f"the variant '{hh.variant}' is not supported")

    custom_fields = _get_and_validate_custom_fields(
        content, hh.create_state().player_count
    )
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
                schema.Schema(
                    lambda n: 0 < n <= player_count,
                    error=f"must be between 1 and {player_count}",
                ),
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
        raise ValidationError('Error validating user-defined "_apm" fields') from e


def _get_hero(
    hole_cards: List[List[Card]], apm_hero: Optional[int]
) -> (int, List[str]):
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
        raise ValidationError(
            "It is unclear who the hero is. You may need to specify _apm_hero ."
        )
    else:
        index = hole_cards_are_known.index(True)
        return index, [repr(c) for c in hole_cards[index]]
