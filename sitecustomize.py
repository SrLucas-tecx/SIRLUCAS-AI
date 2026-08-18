import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(ROOT, "SIRLUCASIA")

for candidate in (ROOT, PROJECT):
    if os.path.isdir(candidate) and candidate not in sys.path:
        sys.path.insert(0, candidate)
