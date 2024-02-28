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
    scenarios = parse_scenario_yml(yml_file)
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
        scenarios = parse_scenario_yml(yml_file)
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
        scenarios = parse_scenario_yml(yml_file)
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
        scenarios = parse_scenario_yml(yml_file)
    assert "Missing key: 'scenario'" in excinfo.value.humanize_error()


def test_ranges_required1():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = """
- game: NLHE
  scenario: Opening
  position: UTG
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        scenarios = parse_scenario_yml(yml_file)
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
        scenarios = parse_scenario_yml(yml_file)
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
        scenarios = parse_scenario_yml(yml_file)
    assert "range can't be empty or null" in excinfo.value.humanize_error()


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
    scenarios = parse_scenario_yml(yml_file)
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
        scenarios = parse_scenario_yml(yml_file)
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
        scenarios = parse_scenario_yml(yml_file)
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
        parse_scenario_yml(yml_file)
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
        parse_scenario_yml(yml_file)
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
        parse_scenario_yml(yml_file)
    err_msg = f"'{invalid_range}' is an invalid range"
    if invalid_range == "":
        err_msg = "range can't be empty or null"
    assert err_msg in str(excinfo.value.humanize_error())


@pytest.mark.parametrize("valid_range", ["22+", "88+; AK", "A4s-ATs", "AK, AQ, AJ"])
def test_valid_ranges(valid_range):
    from anki_poker_master import parse_scenario_yml

    yml_file = f"""
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 72s
    Raise: {valid_range}
""".lstrip()
    scenarios = parse_scenario_yml(yml_file)
    assert len(scenarios[0].ranges["Raise"].hands) > 0


def test_ranges_cant_overlap():
    from anki_poker_master import parse_scenario_yml, ValidationError

    yml_file = f"""
- game: NLHE
  position: UTG
  scenario: Opening
  ranges:
    Call: 77+
    Raise: QQ+
""".lstrip()
    with pytest.raises(ValidationError) as excinfo:
        parse_scenario_yml(yml_file)
    err_msg = (
        "Range for action 'Call' overlaps with range for action "
        + "'Raise' in scenario 'NLHE / Opening / UTG'"
    )
    assert err_msg in excinfo.value.humanize_error()


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
    scenarios = parse_scenario_yml(yml_file)
    assert len(scenarios) == 1
    assert scenarios[0].source == "https://example.com"


def test_default_several():
    """
    Verify that several values can be set as default.
    """
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- DEFAULT: true
  game: NLHE
  scenario: Opening
  source: "https://example.com"

- position: UTG
  ranges:
    Raise: AQ+

- position: HJ
  ranges:
    Raise: AT+
  """.lstrip()
    scenarios = parse_scenario_yml(yml_file)
    assert len(scenarios) == 2
    assert scenarios[0].source == "https://example.com"
    assert scenarios[1].source == "https://example.com"
    assert scenarios[0].game == "NLHE"
    assert scenarios[1].game == "NLHE"
    assert scenarios[0].scenario == "Opening"
    assert scenarios[1].scenario == "Opening"
    assert scenarios[0].position == "UTG"
    assert scenarios[1].position == "HJ"


def test_default_overwrite():
    """
    Verify that a default value can be overwritten.
    """
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- DEFAULT: true
  game: NLHE
  scenario: Opening
  source: "https://example.com"

- position: UTG
  ranges:
    Raise: AQ+

- position: HJ
  scenario: vs. raise from UTG
  ranges:
    Raise: AT+
  """.lstrip()
    scenarios = parse_scenario_yml(yml_file)
    assert len(scenarios) == 2
    assert scenarios[0].source == "https://example.com"
    assert scenarios[1].source == "https://example.com"
    assert scenarios[0].game == "NLHE"
    assert scenarios[1].game == "NLHE"
    assert scenarios[0].scenario == "Opening"
    assert scenarios[1].scenario == "vs. raise from UTG"
    assert scenarios[0].position == "UTG"
    assert scenarios[1].position == "HJ"


def test_default_ranges():
    """
    Verify that default ranges are applied but only if no ranges are
    specified (e.g. you cannot only overwrite the 'Raise' range).
    If necessary, this could be implemented but it's not for simplicity right
    now.
    """
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- DEFAULT: true
  game: NLHE
  scenario: Opening
  source: "https://example.com"
  ranges:
    Raise: AQ+
    Call: 22-77

- position: UTG

- position: HJ

- position: CO
  ranges:
    Call: 98+
  """.lstrip()
    scenarios = parse_scenario_yml(yml_file)
    assert len(scenarios) == 3
    for s in scenarios:
        assert s.source == "https://example.com"
        assert s.game == "NLHE"
        assert s.scenario == "Opening"
    assert scenarios[0].position == "UTG"
    assert scenarios[1].position == "HJ"
    assert scenarios[2].position == "CO"
    assert scenarios[0].ranges.keys() == {"Call", "Raise", "Fold"}
    assert scenarios[1].ranges.keys() == {"Call", "Raise", "Fold"}
    assert scenarios[2].ranges.keys() == {"Call", "Fold"}
