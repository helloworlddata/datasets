"""
Draft code on wrangling NYPD stop frisk data; notes TK

- For all CSV files (previously downloaded) in /tmp/nypd-stopandfrisks:
    - create a new CSV file in which:
        - excess whitespace is trimmed
        - Y/N fields are 'Y' or 'N'
        - less-useful columns are omitted
        - datetime is cleaned via regex and formatted as UTC
        - use-of-force columns consolidated to a Y/N `was_force_used`
        - Convert X/Y to long/lat via "ESRI:102718"
"""
from pathlib import Path
import csv
import re
import pyproj


from sys import argv, path as syspath
syspath.append(str(Path(__file__).resolve().parents[1]))
from data_settings import FETCHED_CSV_DIR as SRC_DIR, WRANGLED_DATA_DIR as DEST_DIR


# Set up the projection
# http://gis.stackexchange.com/a/181673/37839
NYSP1983_PROJ = pyproj.Proj(init="ESRI:102718", preserve_units=True)
# usage:
# long, lat = NYSP1983_PROJ(x, y, inverse=True)

### the main function


DERIVED_HEADERS = [ 'datetime_stop', 'frisked', 'searched', 'arstmade', 'sumissue',
                    'gun_found', 'other_found','was_force_used', 'forceuse_reason',
                    'ac_ongoing_report', 'ac_miscellaneous', 'longitude', 'latitude',]

STOP_REASON_HEADERS = ['cs_objcs', 'cs_descr', 'cs_casng', 'cs_lkout', 'cs_cloth',
                       'cs_drgtr', 'cs_furtv', 'cs_vcrim', 'cs_bulge', 'cs_other',]

BOILERPLATE_HEADERS = ['race', 'age',  'sex', 'weight', 'year', 'ser_num', 'pct', 'beat', 'sector',
                        'xcoord', 'ycoord', 'addrpct', 'addrnum', 'stname', 'stinter', 'crossst',
                        'premname','arstoffn', 'sumoffen', 'crimsusp', 'detailcm',]

# these are all consolidated under was_force_used
FORCE_HEADERS = ['pf_hands', 'pf_wall', 'pf_grnd', 'pf_drwep', 'pf_ptwep', 'pf_baton', 'pf_hcuff', 'pf_pepsp', 'pf_other']
# consolidated under ac_miscellaneous
MISC_AC_HEADERS = ['ac_assoc', 'ac_cgdir', 'ac_evasv', 'ac_incid', 'ac_other', 'ac_proxm', 'ac_stsnd', 'ac_time']
ALL_HEADERS = DERIVED_HEADERS + STOP_REASON_HEADERS + BOILERPLATE_HEADERS



def extract_boilerplate_attrs(row):
    x = {}
    x = {h: row[h] for h in BOILERPLATE_HEADERS}
    x['frisked'] = yes_no(row['frisked'])
    x['searched'] = yes_no(row['searched'])
    x['arstmade'] = yes_no(row['arstmade'])
    x['sumissue'] = yes_no(row['sumissue'])
    x['forceuse_reason'] = row.get('forceuse') # only later years have this column
    return x

def derive_weapon_found_attrs(row):
    x = {}
    x['gun_found'] = next((row[c] for c in ['asltweap', 'machgun', 'pistol', 'riflshot'] if row[c] == 'Y'), 'N')
    x['other_found'] = next((row[c] for c in ['contrabn', 'knifcuti', 'othrweap'] if row[c] == 'Y'), 'N')
    return x

def extract_additional_circumstance_attrs(row):
    # additional circumstances
    # "ac_ongoing_report"
    # - ac_inves - ADDITIONAL CIRCUMSTANCES - ONGOING INVESTIGATION
    # - ac_rept - ADDITIONAL CIRCUMSTANCES - REPORT BY VICTIM/WITNESS/OFFICER
    x = {}
    x['ac_ongoing_report'] = next((row[c] for c in ['ac_inves', 'ac_rept'] if row[c] == 'Y'), 'N')
    x['ac_miscellaneous'] = next((row[c] for c in MISC_AC_HEADERS if row[c] == 'Y'), 'N')
    return x

def extract_reasons_for_stop(row):
    # Reason for stop - let's record all of them
    return {c: yes_no(row[c]) for c in STOP_REASON_HEADERS}

def derive_was_force_used(row):
    """
    Returns 'Y' if any of the row's values for force-related attributes is 'Y';
    otherwise, returns 'N'"""
    return next((row[c] for c in FORCE_HEADERS if row[c] == 'Y'), 'N')


def derive_datetime_stop(datestop, timestop):
    if len(timestop) >= 3:
        # 318 => (03:18)
        # 15:12 => (15:12)
        clean_timestop = "{hrs}:{min}".format(hrs=timestop[0:2].rjust(2, '0'),
                                              min=timestop[2:].rjust(2, '0'))
    else:
        # 5  => (00:05)
        # 14 => (00:14)
        # just pad the string and prepend 00 as the hours value
        clean_timestop = "{hrs}:{min}".format(hrs='00',
                                              min=timestop.rjust(2, '0'))

    # Fix date
    # 7042014 => 2014-07-04
    # 12012011 => 2011-12-01
    datestop = datestop.rjust(8, '0')
    cleaned_datestop = '{yr}-{mth}-{day} {time}'.format(yr=datestop[-4:], mth=datestop[0:2],
                                                        day=datestop[2:4], time=timestop)
    return cleaned_datestop


def project_xy_to_latlng(x, y):
    """
    Projects xcoord and ycoord into longitude and latitude and rounds to 5th-decimal place
    """
    if x and y: # neither are blank
        d = {}
        latlng = NYSP1983_PROJ(int(x), int(y), inverse=True)
        d['longitude'], d['latitude'] = [round(c, 5) for c in latlng]  # round em
        return d
    else:
        return {'longitude': None, 'latitude': None}


def yes_no(v): # helper method to normalize Y/N/'' columns
    return 'Y' if v == 'Y' else 'N'


def strip_record(row):
    # downcase headers,  strip whitespace
    return {k.lower(): v.strip() for k, v in row.items()}

def wrangle_record(row):
    w = {}
    w.update(extract_boilerplate_attrs(row))
    w.update(derive_weapon_found_attrs(row))
    w.update(extract_additional_circumstance_attrs(row))
    w.update(extract_reasons_for_stop(row))
    w.update(project_xy_to_latlng(row['xcoord'], row['ycoord']))
    w['was_force_used'] = derive_was_force_used(row)
    w['datetime_stop'] = derive_datetime_stop(row['datestop'], row['timestop'])
    return w


def read_and_wrangle(src, dest):
    wf = dest.open('w')
    wcsv = csv.DictWriter(wf, fieldnames=ALL_HEADERS)
    wcsv.writeheader()
    # only 2011.csv has windows-1252 instead of ascii encoding,
    # but we open all files as windows-1252 just to be safe
    with src.open("r", encoding='windows-1252') as rf:
        records = csv.DictReader(rf)
        for i, row in enumerate(records):
            row = strip_record(row)
            newrow = wrangle_record(row)
            wcsv.writerow(newrow)
            # a little status checker
            if i % 10000 == 1:
                print("...wrote row #", i)

    # done writing file
    print("Wrangled", i, "rows and saved to", dest)
    wf.close()



if __name__ == '__main__':
    filenames = SRC_DIR.glob('*.csv')
    # optional arguments to parse just select years
    yearstrings = argv[1:] if len(argv) > 1 else []
    if yearstrings:
        print("\n\nWrangling only for the years:", yearstrings, "\n\n")
        filenames = [fn for fn in filenames if any(yr for yr in yearstrings if yr in str(fn))]

    for src_filename in filenames:
        year = re.match(r'^\d{4}', src_filename.name).group()
        dest_filename = DEST_DIR.joinpath('stops-and-frisks--%s.csv' % year)
        print("Wrangling", src_filename, 'into', dest_filename)
        read_and_wrangle(src_filename, dest_filename)
