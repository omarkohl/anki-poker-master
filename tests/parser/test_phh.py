

def test_phh_parser():
    from anki_poker_master.parser.phh import parse_phh

    content = ""
    hand = parse_phh(content)
    assert hand is not None
