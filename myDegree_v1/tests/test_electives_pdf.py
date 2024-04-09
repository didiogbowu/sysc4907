import unittest

from ..scraping.electives_pdf import ElectiveParser


class MyTestCase(unittest.TestCase):
    def test_something(self):
        electives_parser = ElectiveParser()
        pdf_text = (
            "   CLCV 2303  Greek Art and Archaeology *\n"
            "(also listed as ARTH 2102)  ✓\n"
            "E NST 1020  People, Places and Environments\n"  
            "(also listed as GEOG 1020)  ✓ ✓  \n"
            "SOCI 2 160  War and Society  ✓\n"
            "TS ES 4007  Product Life Cycle Analysis  ✓\n"   
            "TSES 4012  Science and Fiction: Creating Tomorrow   ✓\n"
            "SOCI 2450 A  C rime and Society ✓ \n"
            "* CLCV  2303 /ARTH  2102  are no longer eligible  because  it does not have an evaluation of written material\n"
        )  # Some of the lines have erroneous spaces
        course_list = electives_parser.parse(pdf_text)

        expected = ["ENST 1020", "SOCI 2160", "TSES 4007", "TSES 4012", "SOCI 2450A"]
        self.assertEqual(set(expected), set(course_list))
        self.assertFalse("CLCV 2303" in course_list)
        self.assertFalse("ARTH 2102" in course_list)


if __name__ == '__main__':
    unittest.main()
