import http.client
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
import requests
from pypdf import PdfReader

import course_info
import program_tree
import electives_pdf
from parser_interface import Parser

# Departments to scrape courses from
DEPTS = {"SYSC", "ELEC", "ECOR", "CCDP", "COMP",
         "MATH", "PHYS", "CHEM", "BIOL", "CIVE",
         "AERO", "ENVE", "MECH", "MAAE", "SREE"}

# URLs to scrape
DEPT_COURSES_URL = "https://calendar.carleton.ca/undergrad/courses/"
CURRENT_CALENDAR_URL = "https://calendar.carleton.ca/undergrad/undergradprograms/engineering/"
OLD_CALENDAR_URL = "https://calendar.carleton.ca/calendars/YEAR/undergrad/undergradprograms/engineering/"
ELECTIVES_URLS = [
    "https://carleton.ca/engineering-design/current-students/undergrad-academic-support/complementary-studies-electives/",
    "https://carleton.ca/engineering-design/current-students/undergrad-academic-support/comp-electives-for-software-engineering/",
    "https://carleton.ca/engineering-design/current-students/undergrad-academic-support/science-electives/"
]

# Directories to store scraped/parsed files
DEPT_DIR = "departments"
DEPT_HTML_DIR = f"{DEPT_DIR}/raw_html"
PROGRAM_DIR = "programs"
PROGRAM_HTML_DIR = f"{PROGRAM_DIR}/raw_html"
ELECTIVES_DIR = "electives"
ELECTIVES_PDF_DIR = f"{ELECTIVES_DIR}/raw_pdf"


def fetch_page(url: str):
    """
    Fetches the page at the given URL, attempting up to 5 times with exponential backoff.
    Returns the page, or None if the page could not be fetched.
    :param url: URL to fetch
    :return: The page, or None if page could not be fetched
    """
    max_retries = 5
    for attempt in range(max_retries):
        try:
            page = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
            })  # Use random user agent to mitigate blocked requests
            return page
        except (requests.exceptions.ConnectionError, http.client.RemoteDisconnected) as e:
            time.sleep(1.5 ** attempt)  # Exponential backoff if fetch fails
            if attempt >= max_retries - 1:
                print(f"Max retries exceeded. {url} not acquired")
            else:
                print(f"Connection failed, retrying #{attempt}")
    return None


def fetch_and_store(url: str, destination: str, type="html", replace=False) -> None:
    """
    Fetches the page at the given URL and stores it as a html file
    at the given file path. Optionally may replace the file if it
    already exists (skips by default).
    :param url: The url to fetch
    :param destination: The destination file path to store it in
    :param type: The type of file to write. Options are "html" (default), "file" (used for pdfs).
    :param replace: True to replace existing file, False to ignore
    :return: None
    """
    if not os.path.isfile(destination) or replace:
        page = fetch_page(url)
        if page:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            if type == "html":
                with open(destination, "w", encoding="utf-8") as file:
                    file.write(page.text)
            elif type == "file":
                with open(destination, "wb") as file:
                    file.write(page.content)


def scrape_dept_courses(replace=False) -> None:
    """
    Fetches the html for all departments and stores them in the DEPT_HTML_DIR.
    By default, files already present will not be fetched again.
    :param replace: If True (default False), replaces scraped files if existing
    :return: None
    """
    for dept in DEPTS:
        dept_file = f"{DEPT_HTML_DIR}/{dept}.html"
        dept_url = DEPT_COURSES_URL + dept
        fetch_and_store(dept_url, dept_file, replace=replace)


def scrape_program_trees(replace=False) -> None:
    """
    Fetches the html for the last five years from Carleton's website, storing
    the files in the directory specified by global PROGRAM_HTML_DIR.
    By default, files already present will not be fetched again.
    :param replace: If True (default False), replace scraped files if existing
    :return: None
    """
    years = get_catalog_years(5)
    for year in years:
        catalog_file = f"{PROGRAM_HTML_DIR}/{catalog_filename("", year)}.html"
        if year == years[-1]:
            calendar_url = CURRENT_CALENDAR_URL
        else:
            calendar_url = f"{OLD_CALENDAR_URL.replace("YEAR", year)}"
        fetch_and_store(calendar_url, catalog_file, replace=replace)


def scrape_electives(replace=False) -> None:
    """
    Fetches the current PDF elective lists for Complementary Studies, COMP electives,
    and basic science electives, and stores in the directory specified by
    global ELECTIVES_PDF_DIR. Replaces existing files by default.
    :param replace: If True (default False), replaces scraped files if existing
    :return: None
    """
    for elective_urls in ELECTIVES_URLS:
        page = fetch_page(elective_urls)
        if page:
            pdf_link_regex = r"https://.+.pdf"
            pdf_link = re.search(pdf_link_regex, page.text)
            if pdf_link:
                dest = f"{ELECTIVES_PDF_DIR}/{elective_urls.split('/')[-2]}.pdf"
                fetch_and_store(pdf_link.group(), dest, type="file", replace=replace)


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


def scrape_and_parse_all(replace=False):
    """
    Scrape all data for program trees, department courses, and electives lists.
    Perform parsing on them and store the parsed data as JSON files.
    Existing files may optionally be replaced. By default, skips fetching files
    if they already exist.
    :param replace: True to replace existing files, False (default) to skip
    :return: None
    """
    scrape_program_trees(replace=replace)
    scrape_dept_courses(replace=replace)
    scrape_electives(replace=replace)
    course_parser = course_info.CourseInfoParser()
    program_parser = program_tree.ProgramTreeParser()
    electives_parser = electives_pdf.ElectiveParser()

    read_and_parse_dir(DEPT_HTML_DIR, DEPT_DIR, course_parser, "html")
    read_and_parse_dir(PROGRAM_HTML_DIR, PROGRAM_DIR, program_parser, "html")
    read_and_parse_dir(ELECTIVES_PDF_DIR, ELECTIVES_DIR, electives_parser, "pdf")


def read_and_parse_dir(read_dir: str, dest_dir: str, parser: "Parser", file_type: str) -> None:
    """
    Read all files in the read_dir, parse them based on the file_type (either
    'html' or 'pdf'), and store the parsed json in the dest_dir.
    :param parser: The Parser object to use for parsing
    :param read_dir: Directory to read from
    :param dest_dir: Directory to store into
    :param file_type: 'html' or 'pdf'
    :return: None
    """
    if file_type not in ["html", "pdf"]:
        raise ValueError("Type must be 'html' or 'pdf'")

    for file in [f for f in os.listdir(read_dir) if os.path.isfile(os.path.join(read_dir, f))]:
        if file_type == 'html':
            with open(f"{read_dir}/{file}", "r", encoding="utf-8") as source:
                text = source.read()
        elif file_type == 'pdf':
            reader = PdfReader(f"{read_dir}/{file}")
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        data_file = file.replace(".pdf", ".json")
        with open(f"{dest_dir}/{data_file}", "w") as destination:
            result = parser.parse(text)
            destination.write(json.dumps(result, indent=2))


if __name__ == "__main__":
    scrape_and_parse_all()

    # Update eng_electives.json
    # directory = DEPT_HTML_DIR
    # course_scraper = course_info.CourseInfoParser()
    # with open("../mydegree/static/data/eng_electives.json", "r+") as crsfile:
    #     courses = json.loads(crsfile.read())
    #     course_codes = courses.keys()
    #     for dept_file in [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]:
    #         with open(f"{directory}/{dept_file}", "r", encoding="utf-8") as source:
    #             scraped_courses = course_scraper.parse(source.read())
    #             for new_course in scraped_courses:
    #                 if new_course["code"] in course_codes:
    #                     code = new_course["code"]
    #                     if new_course["precludes"]:
    #                         courses[code]["preclusions"] = new_course["precludes"]
    #                     if new_course["prerequisites"]:
    #                         courses[code]["prerequisites"] = new_course["prerequisites"]
    #     crsfile.seek(0)
    #     crsfile.write(json.dumps(courses, indent=2))
    #     crsfile.truncate()

