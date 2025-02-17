import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drugbank.simulator import main

TOTAL_DRUGS=20000
TOTAL_CONSECUTIVE_IDS=19900

if __name__ == "__main__":
    main(TOTAL_DRUGS, TOTAL_CONSECUTIVE_IDS)
