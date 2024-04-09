"""
Module containing the interface Parser.
"""

COURSE_REGEX = r"c?[A-Z]{4} \d{4}"  # Matches course codes. A 'c' prefix is used by parser to indicate concurrent
COURSE_REGEX_SPACELESS = r"[A-Z]{4}\d{4}"  # Matches course codes without spaces
OR_REGEX = f"({COURSE_REGEX},? *)+( *or *{COURSE_REGEX})+"
# Matches strings like:
# - COURSE, COURSE, or COURSE
# - COURSE or COURSE
# accounting for duplicated spaces, oxford comma, and any number of courses


class Parser:
    """
    Interface for parsing strategies (as per Strategy pattern).
    A concrete Parser implements a parse method that takes a string, performs
    parsing specific to the strategy and returns a list of items parsed from the string.
    """
    def parse(self, txt: str) -> list:
        """
        Abstract method to parse a string output and return a list of elements,
        depending on the implementation.
        """
        raise NotImplementedError("Attempt to call abstract parse()")
