import poker
import pytest
import schema


def test_basics():
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
  notes: This is a test
  source: "https://example.com"
""".lstrip()
    scenarios = parse_scenario_yml(yml_file, {})
    assert len(scenarios) == 1
    assert scenarios[0].game == "NLHE"
    assert scenarios[0].position == "UTG"
    assert scenarios[0].scenario == "Opening"
    assert len(scenarios[0].ranges) == 3
    assert scenarios[0].ranges.keys() == {"Call", "Raise", "Fold"}
    assert poker.Hand("A9s") in scenarios[0].ranges["Call"].hands
    assert poker.Hand("A7o") in scenarios[0].ranges["Fold"].hands
    assert poker.Hand("TT") in scenarios[0].ranges["Raise"].hands
    assert scenarios[0].notes == "This is a test"
    assert scenarios[0].source == "https://example.com"


def test_game_required():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- position: UTG
  scenario: Opening
  ranges:
      Call: 98+, A8+, K8+, Q8+, J8+, T8+
      Raise: 88+
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "Missing key: 'game'" in excinfo.value.humanize_error()


def test_position_required():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  scenario: Opening
  ranges:
      Call: 98+, A8+, K8+, Q8+, J8+, T8+
      Raise: 88+
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "Missing key: 'position'" in excinfo.value.humanize_error()


def test_scenario_required():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  position: UTG
  ranges:
      Call: 98+, A8+, K8+, Q8+, J8+, T8+
      Raise: 88+
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "Missing key: 'scenario'" in excinfo.value.humanize_error()


def test_ranges_required1():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  scenario: Opening
  position: UTG
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "Missing key: 'ranges'" in excinfo.value.humanize_error()


def test_ranges_required2():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  scenario: Opening
  position: UTG
  ranges:
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "Key 'ranges' error" in excinfo.value.humanize_error()


def test_ranges_required3():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  scenario: Opening
  position: UTG
  ranges:
    Call:
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "'None' is an invalid range" in excinfo.value.humanize_error()


def test_custom_colors():
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
    My custom range: 22-77
  range_colors:
    Call: "#FF0000"
    My custom range: darkblue
  notes: This is a test
  source: "https://example.com"
""".lstrip()
    scenarios = parse_scenario_yml(yml_file, {})
    assert len(scenarios) == 1


def test_range_color_must_be_str():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
    My custom range: 22-77
  range_colors:
    My custom range: []
  notes: This is a test
  source: "https://example.com"
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "Key 'My custom range' error" in excinfo.value.humanize_error()


def test_range_color_must_be_str2():
    """
    Basic validation test. range_colors must be a mapping from string to
    string.
    """
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
    My custom range: 22-77
  range_colors:
    My custom range:
      - red
      - green
  notes: This is a test
  source: "https://example.com"
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "Key 'My custom range' error" in str(excinfo.value.humanize_error())


def test_range_colors_must_use_valid_ranges():
    """
    'My custom range' is not a valid range name here.
    """
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
  range_colors:
    Call: "#FF0000"
    My custom range: darkblue
  notes: This is a test
  source: "https://example.com"
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        parse_scenario_yml(yml_file, {})
    assert "My custom range" in excinfo.value.humanize_error()


@pytest.mark.parametrize("invalid_color", ["23", "", "#AAAAAAAA"])
def test_range_colors_must_be_valid_color(invalid_color):
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = f"""
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
  range_colors:
    Call: "{invalid_color}"
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        parse_scenario_yml(yml_file, {})
    assert f"'{invalid_color}' is an invalid color" in excinfo.value.humanize_error()


@pytest.mark.parametrize("invalid_range", ["", "GG", "AAA", "-12"])
def test_invalid_ranges(invalid_range):
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = f"""
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: {invalid_range}
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        parse_scenario_yml(yml_file, {})
    err_msg = f"'{invalid_range}' is an invalid range"
    if invalid_range == "":
        # For some reason poker.Range interprets an empty string as None.
        err_msg = "'None' is an invalid range"
    assert err_msg in str(excinfo.value.humanize_error())


@pytest.mark.parametrize("valid_range", ["22+", "88+; AK", "A4s-ATs", "AK, AQ, AJ"])
def test_valid_ranges(valid_range):
    from anki_poker_master import parse_scenario_yml

    yml_file = f"""
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: {valid_range}
""".lstrip()
    scenarios = parse_scenario_yml(yml_file, {})
    assert len(scenarios[0].ranges["Raise"].hands) > 0


def test_default_source():
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- DEFAULT: true
  source: "https://example.com"
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
    My custom range: 22-77
  """.lstrip()
    scenarios = parse_scenario_yml(yml_file, {})
    assert len(scenarios) == 1
    assert scenarios[0].source == "https://example.com"
