import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aitax import AiTaxAdvisor


if __name__ == "__main__":
    print(AiTaxAdvisor().build_indexes())
