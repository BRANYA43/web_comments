from pathlib import Path

from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent.parent

include('./*.py')
