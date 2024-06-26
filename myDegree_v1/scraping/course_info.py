import re
import unicodedata
from bs4 import BeautifulSoup
import json

from pyparsing import Regex, nested_expr

from parser_interface import Parser, COURSE_REGEX, OR_REGEX


class Node:
    """
    Simple class representing a node in a tree of prerequisites.
    Consists of its data element and a list of children, and can
    produce a dictionary representation of itself.
    """
    def __init__(self, data):
        self._data = data
        self._children = []

    def __str__(self):
        return str(self.to_dict())

    def add_child(self, node: "Node") -> None:
        """
        Add a child to this Node.
        :param node: Node to add
        :return: None
        """
        self._children.append(node)

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of the Node and its children.
        :return: dictionary of self and children
        """
        return {"data": self._data, "children": [child.to_dict() for child in self._children]}


class CourseInfoParser(Parser):
    """
    Concrete Parser that parses course information from HTML text.
    """
    def isolate_groups(self, sample: str) -> (str, dict[str, str]):
        """
        Isolate top-level parenthesized groupings of courses from input sample, returning the string with
        groupings replaced by tokens XXXX 000N (to simulate a course code) and a dictionary of tokens and
        their corresponding groupings.
        :param sample: The string to extract groupings from
        :return: The tokenized string and a dictionary of token-group pairs
        """
        groups = {}
        stack = []
        for i in reversed(range(len(sample))):  # Work in reverse to avoid shifting string indices
            char = sample[i]
            if char == ")":
                stack.append(i)
            elif char == "(":
                if len(stack) > 1:
                    stack.pop()
                elif len(stack) == 1:
                    end_index = stack.pop()
                    start_index = i
                    group = sample[start_index:end_index + 1]
                    if len(re.findall(COURSE_REGEX, group)) > 1:
                        key = f"XXXX {len(groups):>04}"
                        groups[key] = group
                        sample = sample[:start_index] + key + sample[end_index + 1:]  # Replace group with key
                else:
                    print(f"'{sample}'", ": Opening parenthesis without closing parenthesis")
        if stack:
            print(f"'{sample}'", ": Closing parenthesis without opening parenthesis")
        return sample, groups

    def parse(self, page: str) -> list:
        """
        Parse the HTML of the given page for courses and return a list of courses as
        dictionaries containing information including prerequisites and preclusions.
        :param page: HTML text to parse as a string
        :return: A list of course dictionaries
        """
        soup = BeautifulSoup(page, "html.parser")
        courseblocks = soup.findAll(class_="courseblock")
        courses = []
        for course in courseblocks:
            desc = course.find(class_="coursedescadditional")
            if desc is None:
                continue

            code = unicodedata.normalize("NFKD", course.find(class_="courseblockcode").get_text())
            entry = {"code": code,
                     "blurb": course.contents[3].get_text().strip(),
                     "precludes": None,
                     "prerequisites": None,
                     "schedule": None}
            courses.append(entry)

            for line_break in desc.findAll("br"):
                line_break.replaceWith("\n")
            desc_lines = unicodedata.normalize("NFKD", desc.get_text()).split("\n")

            for line in desc_lines:
                if "Preclude" in line:
                    entry["precludes"] = re.findall(COURSE_REGEX, line)
                elif "Prerequisite" in line:
                    entry["prerequisites"] = self.prerequisite_tree(line)
                elif "Lecture" in line:
                    entry["schedule"] = line

        return courses

    def parse_prerequisites(self, req_text: str) -> (str, list):
        """
        Parse the given plain English prerequisites and return
         - a string with courses separated by '&' or '|', e.g. 'SYSC 2006&(SYSC 2320|SYSC 3006)'
         - a list of additional requirements, e.g. ['min grade', 'year standing']
        :param req_text: Prerequisites in plain English
        :return: prerequisites in boolean format, list of additional conditions
        """
        # Determine if special requirements are present
        # Regex pattern to match : brief description of condition
        special_requirements = {
            r"year [(status)(standing)]": "year standing",
            r"Engineering|program|enrol": "program restriction",
            "permission": "department permission",
            "grade": "minimum grade",
            "recommended background": "recommended background",
            "CGPA": "minimum CGPA",
            "may not be taken concurrently": "disallowed courses"
        }
        do_not_parse = ["recommended background", "disallowed courses"]
        conditions = []
        for pattern in special_requirements:
            keyword = re.search(pattern, req_text)
            if keyword:
                descriptor = special_requirements[pattern]
                conditions.append(descriptor)
                if descriptor in do_not_parse:
                    req_text = req_text[:keyword.start()]  # Avoid parsing recommended or disallowed courses

        req_text, groups = self.isolate_groups(req_text)

        # extract OR groups first
        disjoint_blocks = list(re.finditer(OR_REGEX, req_text))
        offset = 0
        reqs = {}
        for block in disjoint_blocks:
            req_text = req_text[:block.start() - offset] + req_text[block.end() - offset:]
            offset += len(block.group())
            courses = re.findall(COURSE_REGEX, block.group())
            reqs[block.end() - offset] = f"({'|'.join(courses)})"

        # Remaining courses are assumed to be all required
        for remaining in re.finditer(COURSE_REGEX, req_text):
            reqs[remaining.end()] = remaining.group()

        # Find concurrent courses and add 'c' to them
        concurrents = [match.start() for match in re.finditer("concurrent", req_text)]
        indices = list(reqs.keys())
        if not indices:
            return "", conditions

        indices.sort()
        for c_pos in concurrents:
            closest_course_i = indices[0]
            for i in reversed(indices):
                closest_course_i = i
                if i < c_pos:
                    break
            for course in reversed(list(re.finditer(COURSE_REGEX, reqs[closest_course_i]))):
                text = reqs[closest_course_i]
                reqs[closest_course_i] = text[:course.start()] + "c" + text[course.start():]

        # Search text between each course for patterns that indicate separation between groups
        separator_patterns = [
            " or ",  # OR groups have already been extracted, remaining or indicates separation
            r"\. "   # end of sentence
        ]
        req_groups = [[]]
        for i in range(len(indices) - 1):
            start = indices[i]
            end = indices[i + 1]
            filler = req_text[start:end]
            req_groups[-1].append(reqs[start])
            for pattern in separator_patterns:
                separator = re.search(pattern, filler)
                if separator:
                    req_groups.append([])
            if i == len(indices) - 2:
                req_groups[-1].append(reqs[end])

        if len(req_groups) > 1:
            joinstrings = ["&".join(group) for group in req_groups]
            reqstring = "|".join([string for string in joinstrings if string])
        else:
            reqstring = "&".join(reqs.values())

        for token in groups:
            group, _ = self.parse_prerequisites(groups[token][1:-1])  # Strip surrounding parentheses, then recurse
            replace_index = reqstring.find(token)
            if reqstring[replace_index - 1] == "c":
                # Group becomes concurrent
                group = re.sub(COURSE_REGEX, lambda course_code: f"c{course_code.group()}", group)
                reqstring = reqstring[:replace_index - 1] + group + reqstring[replace_index + len(token):]
                reqstring = f"({reqstring})"
            else:
                reqstring = reqstring.replace(token, group)

        return reqstring, conditions

    def build_tree(self, elements: list, stack: list = None):
        """
        Build a tree of Nodes from the given list of elements.
        Returns the root Node element.
        An initial stack may be provided for the algorithm to use,
        though this defaults to an empty list.
        :param elements:
        :param stack: An initial stack to use (default to empty list)
        :return: The root Node in a tree of Nodes
        """
        if stack is None:
            stack = []
        if elements:
            for i in range(len(elements)):
                if elements[i] == "&" or elements[i] == "|":
                    # Operator node
                    root = Node(elements[i])
                    root.add_child(stack.pop())
                    stack.append(root)
                elif type(elements[i]) is list:
                    # Compound expression
                    subtree = self.build_tree(elements[i], stack=stack)
                    stack.append(subtree)
                else:
                    # Operand node
                    leaf = Node(elements[i])
                    stack.append(leaf)
            root = stack.pop()
            while len(stack) > 0:
                leaf = root
                root = stack.pop()
                root.add_child(leaf)
            return root
        return Node(None)

    def prerequisite_tree(self, req_text: str) -> dict:
        """
        Generate a prerequisite tree for the provided text description.
        The tree is returned in dictionary form so it can be turned into JSON.
        If additional conditions are found in the description, it will also
        contain the keys "conditions" and "text", which contain: a list of
        conditions such as "min grade"; and the original text respectively.
        :param req_text: The plain text prerequisites
        :return: A prerequisite tree as a dictionary
        """
        reqstring, conditions = self.parse_prerequisites(req_text)

        word = Regex(COURSE_REGEX)
        expr = nested_expr("(", ")", content=word | "|" | "&")
        if reqstring:
            if reqstring[0] == "(" and reqstring[-1] == ")":
                parse = expr.parse_string(reqstring)[0].asList()
            else:
                parse = expr.parse_string(f"({reqstring})")[0].asList()
        else:
            parse = []

        tree = self.build_tree(parse).to_dict()
        if conditions:
            tree["conditions"] = conditions
            tree["text"] = req_text
        return tree


if __name__ == "__main__":
    course_parser = CourseInfoParser()
    with open("departments/raw_html/AERO.html", "r", encoding="utf-8") as f:
        print(json.dumps(course_parser.parse(f.read()), indent=2))
