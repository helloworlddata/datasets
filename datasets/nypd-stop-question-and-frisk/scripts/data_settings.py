from pathlib import Path
FETCHED_DATA_DIR = Path('data', 'fetched')
FETCHED_CSV_DIR = FETCHED_DATA_DIR / 'csv'
FETCHED_CSV_DIR.mkdir(exist_ok=True, parents=True)
FETCHED_ZIP_DIR = FETCHED_DATA_DIR / 'zip'
FETCHED_ZIP_DIR.mkdir(exist_ok=True, parents=True)

WRANGLED_DATA_DIR = Path('data', 'wrangled')
WRANGLED_DATA_DIR.mkdir(exist_ok=True, parents=True)
