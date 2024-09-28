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


def test_example_scenarios(capsys, tmp_path):
    from anki_poker_master.cli import main_with_args
    from anki_poker_master.parser.preflop_scenario import EXAMPLE_SCENARIO_FILE

    scenarios_file = tmp_path / "scenarios.yml"
    main_with_args(["-s", str(scenarios_file), "-e"])
    captured = capsys.readouterr()
    assert "Example scenarios file written to" in captured.out
    assert scenarios_file.exists()
    with open(scenarios_file, "r") as f:
        assert f.read().strip() == EXAMPLE_SCENARIO_FILE.strip()


def test_example_scenarios_only_if_doesnt_exist(capsys, tmp_path):
    from anki_poker_master.cli import main_with_args
    from anki_poker_master.parser.preflop_scenario import EXAMPLE_SCENARIO_FILE

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
    pkg_path = tmp_path / "test.apkg"
    main_with_args(
        [
            "-s",
            str(scenarios_file),
            "-o",
            str(pkg_path),
        ]
    )
    captured = capsys.readouterr()
    assert captured == ("", "")
    assert pkg_path.exists()
    assert pkg_path.stat().st_size > 0


def test_generate_deck_only_if_it_doesnt_exist(capsys, tmp_path):
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
    pkg_path = tmp_path / "test.apkg"
    pkg_path.write_text("existing file")
    with pytest.raises(SystemExit) as e:
        main_with_args(
            [
                "-s",
                str(scenarios_file),
                "-o",
                str(pkg_path),
            ]
        )
    captured = capsys.readouterr()
    assert "The file" in captured.out
    assert "already exists" in captured.out
    assert pkg_path.read_text() == "existing file"


def test_generate_deck_with_tags(capsys, tmp_path):
    """
    The test only verifies that no error is raised and that the file is
    created.
    """
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
    pkg_path = tmp_path / "test.apkg"
    main_with_args(
        [
            "-s",
            str(scenarios_file),
            "-o",
            str(pkg_path),
            "--tags",
            "poker",
            "test",
        ]
    )
    captured = capsys.readouterr()
    assert captured == ("", "")
    assert pkg_path.exists()
    assert pkg_path.stat().st_size > 0


def test_generate_deck_with_custom_range_color(capsys, tmp_path):
    """
    The test only verifies that no error is raised and that the file is
    created.
    """
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
  range_colors:
      Call: lightblue
  notes: This is a test
""".lstrip()
    )
    pkg_path = tmp_path / "test.apkg"
    main_with_args(["-s", str(scenarios_file), "-o", str(pkg_path)])
    captured = capsys.readouterr()
    assert captured == ("", "")
    assert pkg_path.exists()
    assert pkg_path.stat().st_size > 0
