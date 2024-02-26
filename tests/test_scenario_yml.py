import poker
import pytest
import strictyaml


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
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- position: UTG
  scenario: Opening
  ranges:
      Call: 98+, A8+, K8+, Q8+, J8+, T8+
      Raise: 88+
""".lstrip()
    with pytest.raises(strictyaml.YAMLError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "game" in str(excinfo.value)


def test_position_required():
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- game: NLHE
  scenario: Opening
  ranges:
      Call: 98+, A8+, K8+, Q8+, J8+, T8+
      Raise: 88+
""".lstrip()
    with pytest.raises(strictyaml.YAMLError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "position" in str(excinfo.value)


def test_scenario_required():
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- game: NLHE
  position: UTG
  ranges:
      Call: 98+, A8+, K8+, Q8+, J8+, T8+
      Raise: 88+
""".lstrip()
    with pytest.raises(strictyaml.YAMLError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "scenario" in str(excinfo.value)


def test_ranges_required1():
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- game: NLHE
  scenario: Opening
  position: UTG
""".lstrip()
    with pytest.raises(strictyaml.YAMLError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "ranges" in str(excinfo.value)


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
    """
    Basic validation test. StrictYAML does not allow specifying dicts
    and lists in "flow style" i.e. using curly and square brackets.
    """
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
    My custom range: []
  notes: This is a test
  source: "https://example.com"
""".lstrip()
    with pytest.raises(strictyaml.YAMLError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})


def test_range_color_must_be_str2():
    """
    Basic validation test. range_colors must be a mapping from string to
    string.
    """
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
    My custom range:
      - red
      - green
  notes: This is a test
  source: "https://example.com"
""".lstrip()
    with pytest.raises(strictyaml.YAMLError) as excinfo:
        scenarios = parse_scenario_yml(yml_file, {})
    assert "found a sequence" in str(excinfo.value)


def test_range_colors_must_use_valid_ranges():
    """
    'My custom range' is not a valid range name here.
    """
    from anki_poker_master import parse_scenario_yml

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
    with pytest.raises(ValueError) as excinfo:
        parse_scenario_yml(yml_file, {})
    assert "My custom range" in str(excinfo.value)


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
