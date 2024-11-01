import pytest


def test_validate_max_number_questions(testdata_dir, golden_dir, pytestconfig):
    """
    Test that an error is returned if the maximum supported number of question
    (study spots) is exceeded. This currently is 20 since it seems unlikely that
    a hand history will have more than 20 study spots. The way the Anki note
    type works it needs a fixed number of fields, so we need to know the
    maximum number of questions in advance. If this number is exceeded, the
    hand history must be split into multiple hands.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.presenter.anki.phh import get_note

    content_long_history = testdata_dir / "hand_history_long.phh"

    hand_long = parse(content_long_history.read_text())

    with pytest.raises(ValueError) as excinfo:
        get_note(hand_long)

    assert "This hand has too many study spots 24." in excinfo.value.args[0]

    content_split_history_1 = testdata_dir / "hand_history_split_1.phh"
    hand_split_1 = parse(content_split_history_1.read_text())
    (note_split_1, media_files_split_1) = get_note(hand_split_1)
    assert len(note_split_1.cards) == 18  # 18 question (study spots)

    content_split_history_2 = testdata_dir / "hand_history_split_2.phh"
    hand_split_2 = parse(content_split_history_2.read_text())
    (note_split_2, media_files_split_2) = get_note(hand_split_2)
    assert len(note_split_2.cards) == 6  # 6 questions (study spots)
