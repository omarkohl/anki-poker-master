import random
from typing import Set, List, Tuple, Optional

from genanki import Note, Deck

from anki_poker_master.model.hand import Hand
from anki_poker_master.presenter.anki import BASIC_MODEL
from anki_poker_master.presenter.html import phh as html_phh


def get_question(
        hand: Hand,
        street_index_for_question: int,
        question_index: int,
        tags: Optional[List[str]] = None,
) -> Note:
    # also rely on html.get_question for validation
    html_question = html_phh.get_question(hand, street_index_for_question, question_index)

    note = Note(
        model=BASIC_MODEL,
        fields=[
            html_question,
            hand.streets[street_index_for_question].questions[question_index].answer,
            hand.notes,
            hand.source,
        ],
        tags=tags or [],
    )
    return note


def get_deck(
        hands: List[Hand],
        tags: Optional[List[str]] = None,
) -> Tuple[Deck, Set[str]]:
    all_media_files = set()
    deck = Deck(
        random.randrange(1 << 30, 1 << 31),
        "AnkiPokerMaster::HandHistory"
    )
    for hand in hands:
        all_media_files.update([f"apm-card-small-{c}.png" for c in hand.hero_cards])
        for i, s in enumerate(hand.streets):
            all_media_files.update([f"apm-card-small-{c}.png" for c in s.board])
            for j, q in enumerate(s.questions):
                deck.add_note(get_question(hand, i, j, tags=tags))
    return deck, all_media_files
