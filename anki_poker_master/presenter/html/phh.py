from anki_poker_master.helper import format_n
from anki_poker_master.model.hand import (
    Hand,
    Action,
    BetAction,
    CallAction,
    CheckAction,
    FoldAction,
    RaiseAction,
)


def _action_to_html(action: Action) -> str:
    css_classes = []
    content = str(action)
    if isinstance(action, CheckAction):
        css_classes.append("check-action")
    elif isinstance(action, RaiseAction):
        css_classes.append("raise-action")
    elif isinstance(action, FoldAction):
        css_classes.append("fold-action")
    elif isinstance(action, BetAction):
        css_classes.append("bet-action")
    elif isinstance(action, CallAction):
        css_classes.append("call-action")
    else:
        raise ValueError(f"Unexpected action: {action}")

    if isinstance(action, (CallAction, RaiseAction, BetAction)):
        if action.is_all_in():
            css_classes.append("all-in-action")

    return f'<span class="{" ".join(css_classes)}">{content}</span>'


def get_question(
    hand: Hand, street_index_for_question: int, question_index: int
) -> str:
    """
    Return the HTML representation of the hand ending at the question identified
    by the street and question index.
    """
    hand.validate_with_indices(street_index_for_question, question_index)

    result = f"""<div class="hand-history">
<h1>{hand.title}</h1>
"""
    if hand.context:
        result += f"<p>{hand.context}</p>\n"
    result += '<div class="pocket-cards">\n'
    for c in hand.hero_cards:
        result += f'<img src="apm-card-small-{c}.png" alt="{c}" title="{c}">\n'
    result += "</div>\n"
    result += f"<p><strong>Hero:</strong> {hand.get_hero().name}</p>\n"
    result += get_question_only(hand, street_index_for_question, question_index)
    result += "</div>\n"
    return result


def get_question_only(
    hand: Hand, street_index_for_question: int, question_index: int
) -> str:
    hand.validate_with_indices(street_index_for_question, question_index)

    result = ""
    table_is_done = False
    question = None

    for street_i, street in enumerate(hand.streets):
        is_last_street = street_index_for_question == street_i
        if table_is_done:
            break
        if is_last_street:
            question = street.questions[question_index]
            max_num_actions = question.action_table_indices[1] + 1
        else:
            max_num_actions = max(len(r) for r in street.actions)
        result += f"<h2>{street.name}</h2>\n"
        if len(street.initial_pots) == 1:
            pot_str = format_n(street.initial_pots[0])
        else:
            pot_str = f"[ {' | '.join(map(format_n, street.initial_pots))} ]"
        result += f"<p>Pot: {pot_str}</p>\n"
        if street.board:
            result += '<div class="board">\n'
            for c in street.board:
                result += f'<img src="apm-card-small-{c}.png" alt="{c}" title="{c}">\n'
            result += "</div>\n"
        result += '<table class="player-actions">\n'
        result += "<thead>\n"
        result += "<tr>\n"
        result += '<th scope="col">Player</th>\n'
        result += '<th scope="col">Stack</th>\n'
        result += f'<th scope="col" colspan="{max_num_actions}">Actions</th>\n'
        result += "</tr>"
        result += "</thead>\n"
        result += "<tbody>\n"
        for i in range(len(street.actions)):
            player_index = (i + street.first_player_actions) % len(hand.players)
            player = hand.players[player_index]
            row_classes = []
            if player.is_hero:
                row_classes.append("hero")
            if not street.initial_players[player_index]:
                row_classes.append("not-playing")
            if row_classes:
                result += f'<tr class="{", ".join(row_classes)}">\n'
            else:
                result += "<tr>\n"
            result += f"<td>{player.name}"
            if player.is_dealer:
                result += ' <span class="dealerbtn">D</span>'
            result += "</td>\n"
            result += f"<td>{format_n(street.initial_stacks[player_index])}</td>\n"
            for j in range(max_num_actions):
                action: str
                if is_last_street:
                    if j > question.action_table_indices[1]:
                        # avoid giving hints how many more actions are to come
                        break
                    if question.action_table_indices == (i, j):
                        action = '<span class="question-action">?</span>'
                        table_is_done = True
                    elif j < len(street.actions[i]) and (
                        j < question.action_table_indices[1]
                        or i < question.action_table_indices[0]
                    ):
                        action = _action_to_html(street.actions[i][j])
                    else:
                        action = ""
                else:  # not last street
                    if j < len(street.actions[i]):
                        action = _action_to_html(street.actions[i][j])
                    else:
                        action = ""
                result += f"<td>{action}</td>"
            result += "</tr>\n"
        result += "</tbody>\n"
        result += "</table>\n"

    result += f"""<p>
<strong>{question.question}</strong>
</p>
"""
    return result
