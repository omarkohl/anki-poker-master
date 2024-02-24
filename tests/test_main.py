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


def test_example_config(capsys, tmp_path):
    from anki_poker_master.cli import main_with_args, EXAMPLE_CONFIG_FILE

    config_file = tmp_path / "config.yml"
    main_with_args(["-c", str(config_file), "-e"])
    captured = capsys.readouterr()
    assert "Example configuration file written to" in captured.out
    assert config_file.exists()
    with open(config_file, "r") as f:
        assert f.read().strip() == EXAMPLE_CONFIG_FILE.strip()


def test_example_scenarios(capsys, tmp_path):
    from anki_poker_master.cli import main_with_args, EXAMPLE_SCENARIO_FILE

    scenarios_file = tmp_path / "scenarios.yml"
    main_with_args(["-s", str(scenarios_file), "-e"])
    captured = capsys.readouterr()
    assert "Example scenarios file written to" in captured.out
    assert scenarios_file.exists()
    with open(scenarios_file, "r") as f:
        assert f.read().strip() == EXAMPLE_SCENARIO_FILE.strip()


def test_example_config_and_scenarios(capsys, tmp_path):
    from anki_poker_master.cli import (
        main_with_args,
        EXAMPLE_CONFIG_FILE,
        EXAMPLE_SCENARIO_FILE,
    )

    config_file = tmp_path / "config.yml"
    scenarios_file = tmp_path / "scenarios.yml"
    main_with_args(["-c", str(config_file), "-s", str(scenarios_file), "-e"])
    captured = capsys.readouterr()
    assert "Example configuration file written to" in captured.out
    assert "Example scenarios file written to" in captured.out
    assert config_file.exists()
    assert scenarios_file.exists()
    with open(config_file, "r") as f:
        assert f.read().strip() == EXAMPLE_CONFIG_FILE.strip()
    with open(scenarios_file, "r") as f:
        assert f.read().strip() == EXAMPLE_SCENARIO_FILE.strip()


def test_example_config_only_if_doesnt_exist(capsys, tmp_path):
    from anki_poker_master.cli import main_with_args, EXAMPLE_CONFIG_FILE

    config_file = tmp_path / "config.yml"
    config_file.write_text("existing file")
    with pytest.raises(SystemExit) as e:
        main_with_args(["-c", str(config_file), "-e"])
    captured = capsys.readouterr()
    assert "The file" in captured.out
    assert "already exists" in captured.out


def test_example_scenarios_only_if_doesnt_exist(capsys, tmp_path):
    from anki_poker_master.cli import main_with_args, EXAMPLE_SCENARIO_FILE

    scenarios_file = tmp_path / "scenarios.yml"
    scenarios_file.write_text("existing file")
    with pytest.raises(SystemExit) as e:
        main_with_args(["-s", str(scenarios_file), "-e"])
    captured = capsys.readouterr()
    assert "The file" in captured.out
    assert "already exists" in captured.out


def test_generate_deck(capsys, tmp_path):
    from anki_poker_master.cli import main_with_args

    scenarios_file = tmp_path / "scenarios.yml"
    scenarios_file.write_text(
        """
- game: NLHE
  position: UTG
  scenario: Top left
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
  notes: This is a test
""".lstrip()
    )
    config_file = tmp_path / "config.yml"
    config_file.write_text(
        """
deck_name: Test Deck
tags:
  - test
""".lstrip()
    )
    deck_file = tmp_path / "Test Deck.apkg"
    main_with_args(
        [
            "-s",
            str(scenarios_file),
            "-n",
            "Test Deck",
            "-d",
            str(tmp_path),
            "-c",
            str(config_file),
        ]
    )
    captured = capsys.readouterr()
    assert captured == ("", "")
    assert deck_file.exists()
    assert deck_file.stat().st_size > 0
