import random
from hashlib import sha256
from typing import Set, List, Tuple, Optional

from genanki import Note, Deck

from anki_poker_master.model.hand import Hand
from anki_poker_master.presenter.anki import (
    HAND_HISTORY_MODEL,
    HAND_HISTORY_MODEL_MAX_NUM_QUESTIONS,
)
from anki_poker_master.presenter.html import phh as html_phh


def get_deck(
    hands: List[Hand],
    tags: Optional[List[str]] = None,
) -> Tuple[Deck, Set[str]]:
    all_media_files = set()
    deck = Deck(random.randrange(1 << 30, 1 << 31), "AnkiPokerMaster::HandHistory")
    for hand in hands:
        note, media_files = get_note(hand, tags=tags)
        all_media_files.update(media_files)
        deck.add_note(note)
    return deck, all_media_files


def get_note(
    hand: Hand,
    tags: Optional[List[str]] = None,
) -> (Note, Set[str]):
    hand.validate()
    all_media_files = set()
    all_media_files.update([f"apm-card-small-{c}.png" for c in hand.hero_cards])
    hero_cards = "\n".join(
        f'<img src="apm-card-small-{c}.png" alt="{c}" title="{c}">'
        for c in hand.hero_cards
    )
    question_answers: List[Tuple[str, str]] = []
    for i, street in enumerate(hand.streets):
        all_media_files.update([f"apm-card-small-{c}.png" for c in street.board])
        for j, question in enumerate(street.questions):
            html_question = html_phh.get_question_only(hand, i, j)
            question_answers.append((html_question, question.answer))

    if len(question_answers) > HAND_HISTORY_MODEL_MAX_NUM_QUESTIONS:
        raise ValueError(
            f"This hand has too many study spots {len(question_answers)}. "
            f"You must split it into multiple hands."
        )

    while len(question_answers) < HAND_HISTORY_MODEL_MAX_NUM_QUESTIONS:
        question_answers.append(("", ""))

    flat_qa = [x for qa in question_answers for x in qa]
    content_hash = sha256(
        "".join(f"{q}{a}" for q, a in question_answers).encode("utf-8")
    ).hexdigest()

    note = Note(
        model=HAND_HISTORY_MODEL,
        fields=[
            (
                "This fields exists to avoid duplicate warnings in Anki. You can "
                + "ignore it. SHA256 of all QA pairs: "
                + content_hash
            ),
            hand.title,
            hand.context,
            hero_cards,
            hand.get_hero().name,
            *flat_qa,
            hand.notes,
            hand.source,
        ],
        tags=tags or [],
    )
    return note, all_media_files
