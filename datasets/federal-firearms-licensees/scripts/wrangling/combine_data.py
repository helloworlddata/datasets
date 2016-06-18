"""
Combines all .txt files in the fetched/ directory and creates
 wrangled/combined.csv

- Replaces 'NULL' with ''
- Adds year and month and yearmonth columns to the data
"""
from sys import argv, path as syspath
from pathlib import Path
syspath.append(str(Path(__file__).resolve().parents[1]))
# end boilerplate
from data_settings import DATA_DIRS
from csv import reader, writer
import re
SRC_DIR = DATA_DIRS['fetched']
DEST_PATH = DATA_DIRS['wrangled'] / 'combined.csv'

wf = DEST_PATH.open('w')
wcsv = writer(wf)

for srcpath in DATA_DIRS['fetched'].glob('*.txt'):
    print(srcpath)
    year, month = srcpath.stem.split('-')
    rows = list(reader(srcpath.read_text().splitlines(), delimiter='\t'))
    if wf.tell() == 0:
        wcsv.writerow(['year', 'month', 'yearmonth'] + rows[0])
    for row in rows[2:]:
        cleaned_row = ['' if col == 'NULL' else col for col in row]
        wcsv.writerow([year, month, '{0}-{1}'.format(year, month)] + cleaned_row)
