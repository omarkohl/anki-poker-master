from anki_poker_master.helper import format_n
from anki_poker_master.model import ValidationError
from anki_poker_master.model.hand import Hand


def get_question(
    hand: Hand, street_index_for_question: int, question_index: int
) -> str:
    """
    Return the HTML representation of the hand ending at the question identified
    by the street and question index.
    """
    # validation
    all_heroes = [p.name for p in hand.players if p.is_hero]
    if len(all_heroes) > 1:
        raise ValidationError(
            "there are multiple heroes, namely " + ", ".join(all_heroes)
        )
    elif len(all_heroes) == 0:
        raise ValidationError("there is no hero")
    else:
        pass  # success

    all_dealers = [p.name for p in hand.players if p.is_dealer]
    if len(all_dealers) > 1:
        raise ValidationError(
            "there are multiple dealers, namely " + ", ".join(all_dealers)
        )
    elif len(all_dealers) == 0:
        raise ValidationError("there is no dealer")
    else:
        pass  # success

    if (
        not hand.streets
        or street_index_for_question < 0
        or street_index_for_question >= len(hand.streets)
    ):
        raise ValidationError(
            f"there is no street with index {street_index_for_question}"
        )

    if (
        not hand.streets[street_index_for_question].questions
        or question_index < 0
        or question_index >= len(hand.streets[street_index_for_question].questions)
    ):
        raise ValidationError(
            f"there is no question with index {question_index} "
            f"in street {hand.streets[street_index_for_question].name}"
        )

    result = f"""<div class="hand-history">
<h1>{hand.title}</h1>
"""
    if hand.context:
        result += f"<p>{hand.context}</p>\n"
    result += '<div class="pocket-cards">\n'
    for c in hand.hero_cards:
        result += f'<img src="apm-card-small-{c}.png" alt="{c}" title="{c}">\n'
    result += "</div>\n"
    result += f"<p><strong>Hero:</strong> {all_heroes[0]}</p>\n"

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
        result += "<th>Player</th>\n"
        result += "<th>Stack</th>\n"
        result += f'<th colspan="{max_num_actions}">Actions</th>\n'
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
                        action = "?"
                        table_is_done = True
                    elif j < len(street.actions[i]) and (
                        j < question.action_table_indices[1]
                        or i < question.action_table_indices[0]
                    ):
                        action = str(street.actions[i][j])
                    else:
                        action = ""
                else:  # not last street
                    if j < len(street.actions[i]):
                        action = str(street.actions[i][j])
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
    result += "</div>\n"
    return result
