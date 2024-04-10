import unittest

from ..scraping import course_info


class HelperFunctionsTestCase(unittest.TestCase):
    def test_isolate_groups(self):
        course_parser = course_info.CourseInfoParser()
        text = "ECOR 2050 and (ECOR 4995 or ECOR 2995) and (SYSC 4907 or SYSC 1234) (may be taken concurrently)"
        result, groups = course_parser.isolate_groups(text)
        self.assertEqual("ECOR 2050 and XXXX 0001 and XXXX 0000 (may be taken concurrently)", result)
        self.assertEqual(
            {
                "XXXX 0000": "(SYSC 4907 or SYSC 1234)",
                "XXXX 0001": "(ECOR 4995 or ECOR 2995)"
            },
            groups
        )

    def test_parse_prerequisites(self):
        course_parser = course_info.CourseInfoParser()
        text = "ECOR 2050 and (ECOR 4995 or ECOR 2995) and (SYSC 4907 or SYSC 1234) (may be taken concurrently)"
        prerequisites, conditions = course_parser.parse_prerequisites(text)
        self.assertEqual("(ECOR 2050&(ECOR 4995|ECOR 2995)&(cSYSC 4907|cSYSC 1234))", prerequisites)
        self.assertEqual([], conditions)

    def test_prerequisite_tree(self):
        course_parser = course_info.CourseInfoParser()
        text = "Prerequisite(s): SYSC 2006 with a minimum grade of C- and (SYSC 2320 or SYSC 3006)."
        course_parser = course_info.CourseInfoParser()
        expected = {
          "data": "&",
          "children": [
            {
              "data": "SYSC 2006",
              "children": []
            },
            {
              "data": "|",
              "children": [
                {
                  "data": "SYSC 2320",
                  "children": []
                },
                {
                  "data": "SYSC 3006",
                  "children": []
                }
              ]
            }
          ],
          "conditions": [
            "minimum grade"
          ],
          "text": "Prerequisite(s): SYSC 2006 with a minimum grade of C- and (SYSC 2320 or SYSC 3006)."
        }
        self.assertEqual(expected, course_parser.prerequisite_tree(text))


if __name__ == '__main__':
    unittest.main()
