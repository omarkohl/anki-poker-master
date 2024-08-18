from pathlib import Path
from pokerkit import HandHistory
from pokerkit import HoleDealing, BoardDealing, CheckingOrCalling, CompletionBettingOrRaisingTo, Folding

def parse_phh(path: Path) -> None:
    with open(path, "rb") as file:
        hh = HandHistory.load(file)

    game = hh.create_game()
    state = hh.create_state()
    print()
    print("START")
    print()
    print("---------")
    print()

    # starting with 1 in both cases
    QUESTION_INDEX = 28  # after which line do you want to ask a question?
    HERO = 7

    operation_index = 0
    hero_cards = ['', '']
    my_status = "SETUP"
    hole_dealing_counter = 0
    action_counter = 0
    for state, action in hh.iter_state_actions():  # I'm assuming number of states always matches number of actions
        if action:
            action_counter += 1
            if action_counter > QUESTION_INDEX:
                print("What do you do?")
                break
        while operation_index < len(state.operations):
            operation = state.operations[operation_index]
            operation_index += 1
            if my_status == "SETUP":
                if isinstance(operation, HoleDealing):
                    my_status = "DEALING"
            if my_status == "DEALING":
                if isinstance(operation, HoleDealing):
                    hole_dealing_counter += 1
                    if operation.player_index == HERO - 1:
                        for i, card in enumerate(operation.cards):
                            if not card.unknown_status:
                                hero_cards[i] = repr(
                                    card,
                                )
                    if hole_dealing_counter == state.player_count:
                        my_status = "START_PREFLOP"
            if my_status == "START_PREFLOP":
                print("Hero is:", hh.players[HERO - 1])
                print("and has cards:", hero_cards)
                blinds = sum(state.blinds_or_straddles)
                pot_amounts = list(state.pot_amounts)
                if not pot_amounts:
                    pot_amounts = [0]
                pot_amounts[0] += blinds
                print("Initial pot is:", pot_amounts)
                print("Players are:", hh.players)
                print("With stacks:", state.stacks)
                print()
                my_status = "PREFLOP"
                continue
            if my_status == "PREFLOP":
                if isinstance(operation, BoardDealing):
                    my_status = "START_FLOP"
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
            if my_status == "START_FLOP":
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
                my_status = "FLOP"
                continue
            if my_status == "FLOP":
                if isinstance(operation, BoardDealing):
                    my_status = "START_TURN"
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
            if my_status == "START_TURN":
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
