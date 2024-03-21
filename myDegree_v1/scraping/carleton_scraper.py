import http.client
import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests

import course_info
# import program_tree

DEPTS = {"SYSC", "ELEC", "ECOR", "CCDP", "COMP",
         "MATH", "PHYS", "CHEM", "BIOL", "CIVE",
         "AERO", "ENVE", "MECH", "MAAE", "SREE"}
PROGRAMS = ["Computer Systems", "Software", "Communications"]

DEPT_COURSES_URL = "https://calendar.carleton.ca/undergrad/courses/"
CURRENT_CALENDAR_URL = "https://calendar.carleton.ca/undergrad/undergradprograms/engineering/"
OLD_CALENDAR_URL = "https://calendar.carleton.ca/calendars/YEAR/undergrad/undergradprograms/engineering/"

DEPT_DIR = "departments"
DEPT_HTML_DIR = f"{DEPT_DIR}/raw_html"
PROGRAM_DIR = "programs"
PROGRAM_HTML_DIR = f"{PROGRAM_DIR}/raw_html"


def fetch_and_store(url: str, destination: str, replace=False) -> None:
    """
    Fetches the page at the given URL and stores it as a html file
    at the given file path. Optionally may replace the file if it
    already exists (skips by default).
    :param url: The url to fetch
    :param destination: The destination file path to store it in
    :param replace: True to replace existing file, False to ignore
    :return: None
    """
    if not os.path.isfile(destination) or replace:

        max_retries = 5
        for attempt in range(max_retries):
            try:
                page = requests.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                })  # Use random user agent to mitigate blocked requests
            except (requests.exceptions.ConnectionError, http.client.RemoteDisconnected) as e:
                time.sleep(1.5 ** attempt)  # Exponential backoff if fetch fails
                if attempt >= max_retries - 1:
                    print(f"Max retries exceeded. {destination} not acquired")
                else:
                    print(f"Connection failed, retrying #{attempt}")
                continue

            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            with open(destination, "w", encoding="utf-8") as file:
                file.write(page.text)
            break


def scrape_dept_courses() -> None:
    """
    Fetches the html for all departments and stores them in the DEPT_HTML_DIR.
    Files already present will not be fetched again.
    :return: None
    """
    for dept in DEPTS:
        dept_file = f"{DEPT_HTML_DIR}/{dept}.html"
        dept_url = DEPT_COURSES_URL + dept
        fetch_and_store(dept_url, dept_file)


def scrape_program_trees() -> None:
    """
    Fetches the html for the last five years from Carleton's website, storing
    the files in the directory specified by global PROGRAM_HTML_DIR.
    Files already present will not be fetched again.
    :return: None
    """
    years = get_catalog_years(5)
    for year in years:
        catalog_file = f"{PROGRAM_HTML_DIR}/{catalog_filename("", year)}.html"
        if year == years[-1]:
            calendar_url = CURRENT_CALENDAR_URL
        else:
            calendar_url = f"{OLD_CALENDAR_URL.replace("YEAR", year)}"
        fetch_and_store(calendar_url, catalog_file)


def catalog_filename(program_name: str, catalog_year: str) -> str:
    """
    Return a filename generated based on the given program and catalog year.
    Filename is generated using the convention Program_Name_Catalog_Year, and does
    *not* include file suffix (e.g., .html, .json). If program name is empty,
    uses "programs" in its place.
    :param program_name: The program name, or an empty string
    :param catalog_year: The catalog year
    :return: The conventional filename for the given parameters
    """
    if program_name:
        return f"{program_name.replace(" ", "_")}_{catalog_year}"
    else:
        return f"programs_{catalog_year}"


def get_catalog_years(years_to_keep: int) -> list[str]:
    """
    Return a list of catalog years (strings in format 20xx-20xx) including
    the current year and the n - 1 preceding years, in ascending order.
    Catalog year is assumed to change after June of every year.
    :param years_to_keep: The number of years back to include
    :return: A list of catalog years
    """
    today = datetime.now()
    start_years = (list(range(today.year - years_to_keep, today.year)) if today.month <= 6
                   else list(range(today.year - years_to_keep + 1, today.year + 1)))
    return [f"{year}-{year + 1}" for year in start_years]


if __name__ == "__main__":
    scrape_program_trees()
    scrape_dept_courses()
    directory = DEPT_HTML_DIR
    with open("../mydegree/static/data/eng_electives.json", "r+") as crsfile:
        courses = json.loads(crsfile.read())
        course_codes = courses.keys()
        for dept_file in [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]:
            with open(f"{directory}/{dept_file}", "r", encoding="utf-8") as source:
                scraped_courses = course_info.scrape_courses(source.read())
                for new_course in scraped_courses:
                    if new_course["code"] in course_codes:
                        code = new_course["code"]
                        if new_course["precludes"]:
                            courses[code]["preclusions"] = new_course["precludes"]
                        if new_course["prerequisites"]:
                            courses[code]["prerequisites"] = new_course["prerequisites"]
        crsfile.seek(0)
        crsfile.write(json.dumps(courses, indent=2))
        crsfile.truncate()
