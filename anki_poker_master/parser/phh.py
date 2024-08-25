from pokerkit import HandHistory

from anki_poker_master.model import ValidationError
from anki_poker_master.model.hand import Hand, Player


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

    state = hh.create_state()

    my_hand = Hand()
    for i in range(state.player_count):
        name = f'p{i + 1}'
        if hh.players:
            name = hh.players[i]
        is_dealer = (i == state.player_count - 1)
        my_hand.players.append(Player(name, is_dealer, False))
    return my_hand
