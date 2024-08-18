#!/usr/bin/env python3

# poetry run python experiment_phh.py /some/path/example.phh

import sys
from anki_poker_master.hand import parse_phh
from pathlib import Path

parse_phh(Path(sys.argv[1]))
