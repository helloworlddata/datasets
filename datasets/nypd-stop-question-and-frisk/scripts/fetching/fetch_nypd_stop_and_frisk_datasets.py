"""
Downloads and unpacks zipped CSV files from the NYPD official data site
"""

from pathlib import Path
from shutil import unpack_archive
from sys import argv, path as syspath
import requests

# http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
syspath.append(str(Path(__file__).resolve().parents[1]))
from data_settings import FETCHED_CSV_DIR, FETCHED_ZIP_DIR


MAX_START_YEAR = 2003
MAX_END_YEAR = 2015
SRC_URLS_FORMAT = 'http://www.nyc.gov/html/nypd/downloads/zip/analysis_and_planning/{year}_sqf_csv.zip'


def fetch_and_save(year):
    zip_url = SRC_URLS_FORMAT.format(year=year)
    print("Downloading", zip_url)
    resp = requests.get(zip_url)

    zip_dest_path = FETCHED_ZIP_DIR.joinpath('{y}.zip'.format(y=year))
    with zip_dest_path.open('wb') as wf:
        print("Writing", zip_dest_path)
        wf.write(resp.content)

    print("Unzipping", zip_dest_path, "to dir:", FETCHED_CSV_DIR)
    unpack_archive(str(zip_dest_path), extract_dir=str(FETCHED_CSV_DIR))


if __name__ == '__main__':
    start_year = MAX_START_YEAR
    end_year = MAX_END_YEAR
    if len(argv) >= 2:
        start_year = int(argv[1])
    if len(argv) is 3:
        end_year = int(argv[2])

    print("Downloading data from:", start_year, 'to', end_year)
    print("======================")
    for year in range(start_year, end_year + 1):
        fetch_and_save(year)


