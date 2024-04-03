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


if __name__ == '__main__':
    unittest.main()
