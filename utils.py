from datetime import datetime
import pathlib
import time
import csv
import os


def get_timestamp():
    current_time = time.time()
    current_timestamp = datetime.fromtimestamp(
        current_time).strftime('%Y-%m-%d %H:%M:%S')

    return current_timestamp


def export_list(slug, output_list):
    path = pathlib.PurePath(os.getcwd())
    file_path = path / 'exports' / slug + '-list-members.csv'

    with open(str(file_path), 'w', newline='') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        for item in output_list:
            wr.writerow([item])

    return file_path


def members_have_ids(source_of_members):
    all_are_ids = all(isinstance(member, int) for member in source_of_members)

    return all_are_ids
