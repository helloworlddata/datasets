"""
Downloads data files from ATF's site, saves them in fetched/YYYY-MM.txt
"""

from sys import argv, path as syspath
from pathlib import Path
syspath.append(str(Path(__file__).resolve().parents[1]))
from data_settings import DATA_DIRS
import requests

FETCHED_DATA_DIR = DATA_DIRS['fetched']

DATA_URLS = {
    '2013-01': "https://www.atf.gov/sites/default/files/legacy/2013/01/08/0113-ffl-list.txt",
    '2014-01': "https://www.atf.gov/resource-center/docs/0114-ffl-listtxt/download",
    '2015-01': "https://www.atf.gov/sites/default/files/legacy/2015/01/22/0115-ffl-list.txt",
    '2016-01': "https://www.atf.gov/firearms/docs/0116-ffl-listtxt/download",
}


def fetch_and_save(*dates):
    """
    Each date argument is a string in YYYY-MM
    """
    for dt in dates:
        url = DATA_URLS[dt]
        print("Downloading: \n\t{0}".format(url))
        resp = requests.get(url)
        if resp.status_code == 200:
            destpath = FETCHED_DATA_DIR.joinpath('{}.txt'.format(dt))
            print("Saving:", destpath)
            destpath.write_text(resp.text)

if __name__ == '__main__':
    if len(argv) < 2:
        dates = list(DATA_URLS.keys())
    else:
        dates = argv[1:]
    fetch_and_save(*dates)
