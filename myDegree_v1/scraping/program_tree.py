import json
import re
from typing import Callable, Any

import unicodedata
from bs4 import BeautifulSoup

from parser_interface import Parser


class ProgramTreeParser(Parser):
    """
    Concrete Parser which parses HTML for program trees of Engineering programs.
    Return a list of dictionaries
    """
    def parse(self, page: str) -> list:
        """
        Parse HTML string  for program trees of Engineering programs and
        :param page:
        :return:
        """
        soup = BeautifulSoup(page, "html.parser")
        tables = soup.findAll(class_="sc_courselist")
        catalog = []
        for prog in tables:
            title = prog.previous_sibling.previous_sibling.text
            if "Bachelor of Engineering" not in title:
                tables.remove(prog)
                continue
            title = re.sub(r"-? ?Bachelor of Engineering ?", "", title)
            title = title[:title.find("(")]

            rows = [tr for tr in prog.findAll("tr")]
            years = self.split_list(rows,
                               lambda tr: re.match(r"First|Second|Third|Fourth year", tr.text) is not None)
            years = [self.split_list(x, lambda x: x.find(class_="hourscol").text, destroy_tokens=False)
                     for x in years]
            for year in range(len(years)):
                for section in range(len(years[year])):
                    for item in range(len(years[year][section])):
                        years[year][section][item] = unicodedata.normalize("NFKD", years[year][section][item].text)
            program_dict = {
                "title": title,
                "catalog": years
            }
            catalog.append(program_dict)
        return catalog

    def split_list(self, lst: list, check_token: Callable[[Any], bool], destroy_tokens=True) -> list:
        """
        Split a given list at delimiter elements, destroying the delimiters by default.
        Delimiter elements are elements which return True when passed to the provided check_token
        function. Return a list whose elements are the remaining fragments of the initial list.
        If destroy_tokens = False, delimiters will be the first element of each list fragment.
        :param lst: The list to split
        :param check_token: A function which takes an element and returns True if it should split on it
        :param destroy_tokens: True if delimiters are to be destroyed in the splitting process
        :return: A list of the split list fragments
        """
        output = []
        split = []
        for elem in lst:
            if check_token(elem):
                if split:
                    output.append(split)
                split = [] if destroy_tokens else [elem]
            else:
                split.append(elem)
        if split:
            output.append(split)
        return output


if __name__ == "__main__":
    program_tree_parser = ProgramTreeParser()
    with open("programs/raw_html/programs_2023-2024.html", "r", encoding="utf-8") as f:
        catalog = program_tree_parser.parse(f.read())
        for program in catalog:
            print(json.dumps(program, indent=2), "\n\n")
