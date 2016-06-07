from data_settings import FETCHED_ZIP_DIR, FETCHED_CSV_DIR
from shutil import unpack_archive
import requests
START_YEAR = 2003
END_YEAR = 2015

SRC_URLS_FORMAT = 'http://www.nyc.gov/html/nypd/downloads/zip/analysis_and_planning/{year}_sqf_csv.zip'


def main():
    for year in range(START_YEAR, END_YEAR + 1):
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
    main()
