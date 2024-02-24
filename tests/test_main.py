import pytest


def test_scenarios_is_required():
    from anki_poker_master.cli import main_with_args

    with pytest.raises(SystemExit) as e:
        main_with_args([])


def test_help(capsys):
    from anki_poker_master.cli import main_with_args

    with pytest.raises(SystemExit) as e:
        main_with_args(["-h"])
    captured = capsys.readouterr()
    assert "AnkiPokerMaster" in captured.out


def test_version(capsys):
    from anki_poker_master.cli import main_with_args

    with pytest.raises(SystemExit) as e:
        main_with_args(["-v"])
    captured = capsys.readouterr()
    assert captured.out.startswith("AnkiPokerMaster")
    assert len(captured.out) > len("AnkiPokerMaster\n")
