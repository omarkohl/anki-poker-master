from numbers import Number
from typing import List, Tuple, Optional

from anki_poker_master.helper import format_n
from anki_poker_master.model import ValidationError


class Action:
    pass


class FoldAction(Action):
    def __str__(self):
        return "F"

    def __eq__(self, other):
        return isinstance(other, FoldAction)


class BetAction(Action):
    _amount: Number
    _is_all_in: bool

    def __init__(self, amount: Number, is_all_in: bool = False) -> None:
        self._amount = amount
        self._is_all_in = is_all_in

    def __str__(self):
        return f"B {format_n(self._amount)}" + (" (AI)" if self._is_all_in else "")

    def __eq__(self, other):
        return (
            isinstance(other, BetAction)
            and self._amount == other._amount
            and self._is_all_in == other._is_all_in
        )

    def is_all_in(self) -> bool:
        return self._is_all_in

    def amount(self) -> Number:
        return self._amount


class RaiseAction(Action):
    _amount: Number
    _is_all_in: bool

    def __init__(self, amount: Number, is_all_in: bool = False) -> None:
        self._amount = amount
        self._is_all_in = is_all_in

    def __str__(self):
        return f"R {format_n(self._amount)}" + (" (AI)" if self._is_all_in else "")

    def __eq__(self, other):
        return (
            isinstance(other, RaiseAction)
            and self._amount == other._amount
            and self._is_all_in == other._is_all_in
        )

    def is_all_in(self) -> bool:
        return self._is_all_in

    def amount(self) -> Number:
        return self._amount


class CheckAction(Action):
    def __str__(self):
        return "X"

    def __eq__(self, other):
        return isinstance(other, CheckAction)


class CallAction(Action):
    _is_all_in: bool

    def __init__(self, is_all_in: bool = False) -> None:
        self._is_all_in = is_all_in

    def __str__(self):
        return "C"

    def __eq__(self, other):
        return isinstance(other, CallAction) and self._is_all_in == other._is_all_in

    def is_all_in(self) -> bool:
        return self._is_all_in


class Question:
    question: str
    answer: str
    action_table_indices: Tuple[int, int]

    def __init__(
        self, question: str, answer: str, action_table_indices: Tuple[int, int]
    ):
        self.question = question
        self.answer = answer
        self.action_table_indices = action_table_indices

    def __eq__(self, other):
        return (
            isinstance(self, other.__class__)
            and self.question == other.question
            and self.answer == other.answer
            and self.action_table_indices == other.action_table_indices
        )

    def __repr__(self):
        return (
            f'Question("{self.question}", "{self.answer}", {self.action_table_indices})'
        )


class Street:
    name: str
    board: List[str]
    initial_pots: List[Number]
    initial_stacks: List[Number]
    initial_players: List[bool]
    first_player_actions: int
    # will start with 'first_player_actions'
    actions: List[List[Action]]
    questions: List[Question]
    # one for every action that the 'hero' takes, only used if no explicit questions are asked
    default_questions: List[Question]

    def __init__(
        self,
        name: str,
        board: List[str],
        initial_pots: List[Number],
        initial_players: List[bool],
        initial_stacks: List[Number],
        first_player_actions: int,
        actions: List[List[Action]],
        questions: Optional[List[Question]] = None,
        default_questions: Optional[List[Question]] = None,
    ):
        self.name = name
        self.board = board
        self.initial_pots = initial_pots
        self.initial_players = initial_players
        self.initial_stacks = initial_stacks
        self.first_player_actions = first_player_actions
        self.actions = actions
        self.questions = questions if questions else []
        self.default_questions = default_questions if default_questions else []

    def __eq__(self, other):
        return (
            isinstance(self, other.__class__)
            and self.name == other.name
            and self.board == other.board
            and self.initial_pots == other.initial_pots
            and self.initial_players == other.initial_players
            and self.initial_stacks == other.initial_stacks
            and self.first_player_actions == other.first_player_actions
            and self.actions == other.actions
            and self.questions == other.questions
            and self.default_questions == other.default_questions
        )


class Player:
    name: str
    is_dealer: bool
    is_hero: bool

    def __init__(self, name: str, is_dealer: bool, is_hero: bool):
        self.name = name
        self.is_dealer = is_dealer
        self.is_hero = is_hero

    def __repr__(self):
        return (
            f'Player("{self.name}", is_dealer={self.is_dealer}, is_hero={self.is_hero})'
        )

    def __eq__(self, other):
        return (
            isinstance(self, other.__class__)
            and self.name == other.name
            and self.is_dealer == other.is_dealer
            and self.is_hero == other.is_hero
        )


class Hand:
    title: str
    # last one is the dealer
    players: List[Player]
    hero_cards: List[str]
    streets: List[Street]
    notes: str
    source: str
    context: str
    answers: List[str]

    def __init__(self):
        self.title: str = ""
        self.players: List[Player] = []
        self.hero_cards: List[str] = ["", ""]
        self.streets: List[Street] = []
        self.notes: str = ""
        self.source: str = ""
        self.context: str = ""
        self.answers: List[str] = []

    def __str__(self):
        return f"{self.title} {self.players} {self.hero_cards} {self.streets} {self.notes} {self.source} {self.context} {self.answers}"

    def validate(self):
        """
        Validate the hand. Raises a ValidationError if the hand is not valid.
        """
        all_heroes = [p.name for p in self.players if p.is_hero]
        if len(all_heroes) > 1:
            raise ValidationError(
                "there are multiple heroes, namely " + ", ".join(all_heroes)
            )
        elif len(all_heroes) == 0:
            raise ValidationError("there is no hero")
        else:
            pass  # success

        all_dealers = [p.name for p in self.players if p.is_dealer]
        if len(all_dealers) > 1:
            raise ValidationError(
                "there are multiple dealers, namely " + ", ".join(all_dealers)
            )
        elif len(all_dealers) == 0:
            raise ValidationError("there is no dealer")
        else:
            pass  # success

    def validate_with_indices(self, street_index_for_question, question_index):
        """
        Validate the hand. Raises a ValidationError if the hand is not valid.
        It executes normal validation plus ensures that the indices are valid.
        """
        self.validate()
        if (
            not self.streets
            or street_index_for_question < 0
            or street_index_for_question >= len(self.streets)
        ):
            raise ValidationError(
                f"there is no street with index {street_index_for_question}"
            )

        if (
            not self.streets[street_index_for_question].questions
            or question_index < 0
            or question_index >= len(self.streets[street_index_for_question].questions)
        ):
            raise ValidationError(
                f"there is no question with index {question_index} "
                f"in street {self.streets[street_index_for_question].name}"
            )

    def get_hero(self):
        """
        Get the hero player. The hand must be validated before calling this
        method.
        """
        return next(p for p in self.players if p.is_hero)
