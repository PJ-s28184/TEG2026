import subprocess
import sys
from pathlib import Path


def main():
    app_path = Path(__file__).resolve().parent / "gui" / "app.py"
    sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", str(app_path)]))

if __name__ == "__main__":
    main()
