from numbers import Number
from typing import List


class Street:
    name: str
    board: List[str]
    initial_pots: List[Number]
    initial_stacks: List[Number]
    initial_players: List[bool]
    first_player: int
    # will start with 'first_player'
    actions: List[List[str]]

    def __init__(self, name, board, initial_pots, initial_players, initial_stacks, first_player, actions):
        self.name = name
        self.board = board
        self.initial_pots = initial_pots
        self.initial_players = initial_players
        self.initial_stacks = initial_stacks
        self.first_player = first_player
        self.actions = actions

    def __eq__(self, other):
        return (
                isinstance(self, other.__class__) and
                self.name == other.name and
                self.board == other.board and
                self.initial_pots == other.initial_pots and
                self.initial_players == other.initial_players and
                self.initial_stacks == other.initial_stacks and
                self.first_player == other.first_player and
                self.actions == other.actions
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
        return f'Player("{self.name}", is_dealer={self.is_dealer}, is_hero={self.is_hero})'


class Hand:
    # last one is the dealer
    players: List[Player]
    hero_cards: List[str]
    streets: List[Street]
    notes: str
    source: str
    context: str

    def __init__(self):
        self.players: List[Player] = []
        self.hero_cards: List[str] = ['', '']
        self.streets: List[Street] = []
        self.notes: str = ''
        self.source: str = ''
        self.context: str = ''

    def __str__(self):
        return f'{self.players} {self.hero_cards} {self.streets} {self.notes} {self.source} {self.context}'
