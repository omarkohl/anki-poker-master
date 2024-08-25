import pytest

from anki_poker_master.model import ValidationError


def test_phh_parser():
    from anki_poker_master.parser.phh import parse_phh

    content = ""
    hand = parse_phh(content)
    assert hand is not None


def test_phh_parser_emtpy_file():
    from anki_poker_master.parser.phh import parse_phh
    with pytest.raises(ValidationError) as excinfo:
        parse_phh("")
    assert "Invalid PHH (empty)" in excinfo.value.humanize_error()


def test_phh_parser_incomplete_file():
    from anki_poker_master.parser.phh import parse_phh
    content = """variant = "NT"
antes = [0, 0, 0, 0, 0, 0, 0, 0, 0]
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "Error parsing PHH with content:" in excinfo.value.humanize_error()
