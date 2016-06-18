from pathlib import Path
DATA_DIR = Path('data')
DATA_DIRS = {
    'fetched': DATA_DIR / 'fetched',
    'wrangled': DATA_DIR / 'wrangled'
}
for k, ddir in DATA_DIRS.items():
    ddir.mkdir(exist_ok=True, parents=True)
