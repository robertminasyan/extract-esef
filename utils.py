import csv
from pathlib import Path
import os
from datetime import datetime


# specify path to archives
# here testing or training archive should be stated
PATH_ARCHIVES = archives = os.path.join(".", "archives_training")
PATH_PARSED = parsed = os.path.join(".", "parsed")
PATH_FAILED = parsed = os.path.join(".", "error")

def to_csv(facts_mapped, facts):
    with open('outputmappedfacts.csv', mode='a', newline='') as file:
        # Create a writer object
        writer = csv.DictWriter(file, fieldnames=['NCRname', 'name', 'entity', 'value', 'measure', 'startDate', 'endDate'])

        # If the file is empty, write the header row
        if file.tell() == 0:
            writer.writeheader()

        # Write the data rows
        for row in facts_mapped:
            namerow = row["name"]
            measure = row["measure"]
            array = measure.split(":")
            if(row.get("startDate")==None or row.get("endDate")==None):
                continue
            if(check_period(row.get("startDate"), row.get("endDate"))):
                writer.writerow({"NCRname": namerow[0], "name": namerow[1], "entity": row["entity"], "value": row["value"], "measure": array[1], "startDate": row["startDate"], "endDate": row["endDate"]})
            else:
                continue
    with open('outputallfacts.csv', mode='a', newline='') as file:

        # Create a writer object
        writer = csv.DictWriter(file, fieldnames=['name','entity', 'value', 'measure', 'startDate', 'endDate'])

        # If the file is empty, write the header row
        if file.tell() == 0:
            writer.writeheader()

        # Write the data rows
        for row in facts:
            if((row.get("startDate")==None) or (row.get("endDate")==None)):
                continue
            if(check_period(row.get("startDate"), row.get("endDate"))):
                writer.writerow({"name": row.get("name"), "entity": row.get("entity"), "value": row.get("value"), "measure": row.get("measure"), "startDate": row.get("startDate"), "endDate": row.get("endDate")})
            else:
                continue

def check_period(startDate, endDate):
    financial_year_start = datetime.strptime("01-01", "%m-%d")
    financial_year_end = datetime.strptime("12-31", "%m-%d")

    start_date = datetime.strptime(startDate, "%Y-%m-%d")
    end_date = datetime.strptime(endDate, "%Y-%m-%d")
    if ((start_date.month == financial_year_start.month and end_date.month == financial_year_end.month) or (start_date.month == financial_year_start.month and end_date.month == financial_year_start.month)):
        return True
    else:
        return False



def write_fail(key, entity):
    # print to text file that a mapping failed
    with open('failedmappings.txt', mode='a') as file:

        file.write(f"'{key}' for '{entity}' did not map, please fix\n")

def move_file_to_parsed(zip_file_path: str, language: str) -> None:
    """Move a file from the filings folder to the parsed folder."""
    final_path = os.path.join(PATH_PARSED, language)
    Path(final_path).mkdir(parents=True, exist_ok=True)

    os.replace(
        zip_file_path,
        os.path.join(final_path, os.path.basename(zip_file_path)),
    )

def move_file_to_error(zip_file_path: str, language: str) -> None:
    """Move a file from the filings folder to the error folder."""
    final_path = os.path.join(PATH_FAILED, language)
    Path(final_path).mkdir(parents=True, exist_ok=True)

    os.replace(
        zip_file_path,
        os.path.join(final_path, os.path.basename(zip_file_path)),
    )

def _path_to_language(subdir: str) -> str:
    """Extract language from path."""
    return subdir.split(os.sep)[-1]
