import pprint
from pathlib import Path
from typing import Optional

from pokerkit import HandHistory
from pokerkit import HoleDealing, BoardDealing, CheckingOrCalling, CompletionBettingOrRaisingTo, Folding
from tomllib import loads

from anki_poker_master.model.hand import Street, Player, Hand


def parse_phh(path: Path) -> None:
    with open(path, "rb") as file:
        hh = HandHistory.load(file)

    with open(path, "rt") as file:
        raw_file = loads(file.read())

    answers = []
    if "_apm_answers" in raw_file:
        answers = raw_file["_apm_answers"]

    hero_index: Optional[int] = None
    if "_apm_hero" in raw_file:
        hero_index = int(raw_file["_apm_hero"])

    game = hh.create_game()
    state = hh.create_state()
    print()
    print("START")
    print()
    print("---------")
    print()

    my_hand = Hand()

    for i in range(state.player_count):
        name = f'p{i+1}'
        if hh.players:
            name = hh.players[i]
        is_dealer = (i == state.player_count - 1)
        my_hand.players.append(Player(name, is_dealer, False))

    pprint.pp(vars(my_hand))
    print()

    question_counter = 0

    operation_index = 0
    hero_cards = ['', '']
    my_status = "SETUP"
    hole_dealing_counter = 0
    there_has_been_a_bet = False
    # TODO modify again to only iterate over states since I don't need the actions
    for state, _ in hh.iter_state_actions():  # I'm assuming number of states always matches number of actions
        while operation_index < len(state.operations):
            operation = state.operations[operation_index]
            operation_index += 1
            if my_status == "SETUP":
                if isinstance(operation, HoleDealing):
                    my_status = "DEALING"
            if my_status == "DEALING":
                if isinstance(operation, HoleDealing):
                    hole_dealing_counter += 1
                    if all(not c.unknown_status for c in operation.cards):
                        if hero_index is None or hero_index - 1 == operation.player_index:
                            my_hand.players[operation.player_index].is_hero = True
                            for i, card in enumerate(operation.cards):
                                my_hand.hero_cards[i] = repr(
                                    card,
                                )
                    if hole_dealing_counter == state.player_count:
                        my_status = "START_PREFLOP"
            if my_status == "START_PREFLOP":
                blinds = sum(state.blinds_or_straddles)
                pot_amounts = list(state.pot_amounts)
                if not pot_amounts:
                    pot_amounts = [0]
                pot_amounts[0] += blinds
                my_hand.streets.append(
                    Street(
                        "Preflop",
                        [],
                        pot_amounts,
                        [True for _ in range(state.player_count)],
                        state.stacks.copy(),
                        2,
                        [[] for _ in range(state.player_count)],
                    )
                )
                pprint.pp(vars(my_hand))
                pprint.pp(vars(my_hand.streets[0]))
                print()
                my_status = "PREFLOP"
                there_has_been_a_bet = False
                continue
            if my_status == "PREFLOP":
                if isinstance(operation, BoardDealing):
                    my_status = "START_FLOP"
                elif isinstance(operation, CheckingOrCalling):
                    my_hand.streets[0].actions[operation.player_index].append("C" if there_has_been_a_bet else "X")
                    print(hh.players[operation.player_index])
                    print("C")
                    print()
                elif isinstance(operation, CompletionBettingOrRaisingTo):
                    my_hand.streets[0].actions[operation.player_index].append(f'{"R" if there_has_been_a_bet else "B"} {operation.amount}')
                    there_has_been_a_bet = True
                    print(hh.players[operation.player_index])
                    print("R", operation.amount)  # why not operation.amount?
                    print()
                elif isinstance(operation, Folding):
                    my_hand.streets[0].actions[operation.player_index].append("F")
                    print(hh.players[operation.player_index])
                    print("F")
                    print()
                else:
                    print(operation.__class__.__name__)
                    print()
                if operation.commentary == "APM":
                    print("What do you do?")
                    if len(answers) > question_counter:
                        print("Answer:", answers[question_counter])
                    question_counter += 1
                    print()
            if my_status == "START_FLOP":
                pprint.pp(vars(my_hand))
                pprint.pp(vars(my_hand.streets[0]))
                print()

                print("Starting the flop with cards:", operation.cards)
                print("And pots:", list(state.pot_amounts))
                active_players = []
                for i, name in enumerate(hh.players):
                    if state.statuses[i]:
                        active_players.append(name)
                print("Players are:", hh.players)
                print("With stacks:", state.stacks)
                print("Active players:", ", ".join(active_players))
                print()
                my_hand.streets.append(
                    Street(
                        "Flop",
                        [repr(c) for c in operation.cards],
                        list(state.pot_amounts),
                        state.statuses.copy(),
                        state.stacks.copy(),
                        0,
                        [[] for _ in range(state.player_count)],
                    )
                )
                pprint.pp(vars(my_hand))
                pprint.pp(vars(my_hand.streets[1]))
                print()

                there_has_been_a_bet = False
                my_status = "FLOP"
                continue
            if my_status == "FLOP":
                if isinstance(operation, BoardDealing):
                    my_status = "START_TURN"
                elif isinstance(operation, CheckingOrCalling):
                    my_hand.streets[1].actions[operation.player_index].append("C" if there_has_been_a_bet else "X")
                    print(hh.players[operation.player_index])
                    print("C")
                    print()
                elif isinstance(operation, CompletionBettingOrRaisingTo):
                    my_hand.streets[1].actions[operation.player_index].append(f'{"R" if there_has_been_a_bet else "B"} {operation.amount}')
                    there_has_been_a_bet = True
                    print(hh.players[operation.player_index])
                    print("R", operation.amount)  # why not operation.amount?
                    print()
                elif isinstance(operation, Folding):
                    my_hand.streets[1].actions[operation.player_index].append("F")
                    print(hh.players[operation.player_index])
                    print("F")
                    print()
                else:
                    print(operation.__class__.__name__)
                    print()
                if operation.commentary == "APM":
                    print("What do you do?")
                    if len(answers) > question_counter:
                        print("Answer:", answers[question_counter])
                    question_counter += 1
                    print()
            if my_status == "START_TURN":
                pprint.pp(vars(my_hand))
                pprint.pp(vars(my_hand.streets[1]))
                print()

                print("Starting the turn with cards:", operation.cards)
                print("And pots:", list(state.pot_amounts))
                active_players = []
                for i, name in enumerate(hh.players):
                    if state.statuses[i]:
                        active_players.append(name)
                print("Players are:", hh.players)
                print("With stacks:", state.stacks)
                print("Active players:", ", ".join(active_players))
                print()
                there_has_been_a_bet = False
                my_status = "TURN"
                continue
            if my_status == "TURN":
                if isinstance(operation, BoardDealing):
                    my_status = "START_RIVER"
                elif isinstance(operation, CheckingOrCalling):
                    print(hh.players[operation.player_index])
                    print("C")
                    print()
                elif isinstance(operation, CompletionBettingOrRaisingTo):
                    print(hh.players[operation.player_index])
                    print("R", operation.amount)  # why not operation.amount?
                    print()
                elif isinstance(operation, Folding):
                    print(hh.players[operation.player_index])
                    print("F")
                    print()
                else:
                    print(operation.__class__.__name__)
                    print()
                if operation.commentary == "APM":
                    print("What do you do?")
                    if len(answers) > question_counter:
                        print("Answer:", answers[question_counter])
                    question_counter += 1
                    print()
            if my_status == "START_RIVER":
                print("Starting the river with cards:", operation.cards)
                print("And pots:", list(state.pot_amounts))
                active_players = []
                for i, name in enumerate(hh.players):
                    if state.statuses[i]:
                        active_players.append(name)
                print("Players are:", hh.players)
                print("With stacks:", state.stacks)
                print("Active players:", ", ".join(active_players))
                print()
                there_has_been_a_bet = False
                my_status = "RIVER"
                continue
            if my_status == "RIVER":
                if isinstance(operation, CheckingOrCalling):
                    print(hh.players[operation.player_index])
                    print("C")
                    print()
                elif isinstance(operation, CompletionBettingOrRaisingTo):
                    print(hh.players[operation.player_index])
                    print("R", operation.amount)  # why not operation.amount?
                    print()
                elif isinstance(operation, Folding):
                    print(hh.players[operation.player_index])
                    print("F")
                    print()
                else:
                    print(operation.__class__.__name__)
                    print()
                if operation.commentary == "APM":
                    print("What do you do?")
                    if len(answers) > question_counter:
                        print("Answer:", answers[question_counter])
                    question_counter += 1
                    print()
