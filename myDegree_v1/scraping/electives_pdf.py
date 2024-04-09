import re

from parser_interface import Parser, COURSE_REGEX_SPACELESS


class ElectiveParser(Parser):
    """
    Parser implementation which parses electives lists from scraped PDFs.
    """
    def parse(self, pdf_text: str):
        """
        Parse the provided text, which should be extracted from the elective list PDF,
        and return a list of the course codes. Will only take course codes if they appear
        at the beginning of a line.
        :param pdf_text: The text to parse
        :return: A list of course codes extracted from the text
        """
        lines = pdf_text.split("\n")
        courses = set()

        for line in lines:
            if "*" not in line:  # Courses marked by asterisks are no longer eligible for CSE
                text = line.replace(" ", "")
                if len(text) >= 10:
                    if text[8].isupper() and not text[9].islower():
                        if re.match(COURSE_REGEX_SPACELESS + "[A-E]", text):  # Include section letter if present
                            courses.add(text[:4] + " " + text[4:9])
                    elif re.match(COURSE_REGEX_SPACELESS, text):
                        courses.add(text[:4] + " " + text[4:8])
        return list(courses)
