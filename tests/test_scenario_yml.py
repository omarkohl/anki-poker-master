import poker


def test_simple():
    from anki_poker_master import parse_scenario_yml

    yml_file = """
- game: NLHE
  position: UTG
  scenario: Top left
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
    assert scenarios[0].scenario == "Top left"
    assert len(scenarios[0].ranges) == 3
    assert scenarios[0].ranges.keys() == {"Call", "Raise", "Fold"}
    assert poker.Hand("A9s") in scenarios[0].ranges["Call"].hands
    assert poker.Hand("A7o") in scenarios[0].ranges["Fold"].hands
    assert poker.Hand("TT") in scenarios[0].ranges["Raise"].hands
    assert scenarios[0].notes == "This is a test"
    assert scenarios[0].source == "https://example.com"
