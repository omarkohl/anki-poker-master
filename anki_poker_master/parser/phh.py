from pokerkit import HandHistory

from anki_poker_master.model import ValidationError
from anki_poker_master.model.hand import Hand


def parse_phh(content: str) -> Hand:
    if not content:
        raise ValidationError("Invalid PHH (empty)")

    my_hand = Hand()

    try:
        hh = HandHistory.loads(content)
    except Exception as e:
        if len(content) > 100:
            content_for_err = content[:100] + "\n..."
        else:
            content_for_err = content
        raise ValidationError(f'Error parsing PHH with content:\n{content_for_err}') from e
    return my_hand
