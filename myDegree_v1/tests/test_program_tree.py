import unittest
from ..scraping import program_tree


class HelperFunctionsTestCase(unittest.TestCase):
    def test_split_list(self):
        program_parser = program_tree.ProgramTreeParser()
        lst = ['x', 1, 2, 'a', 4, 'b', 6, 7]

        def is_char(value):
            return type(value) is str and len(value) == 1

        result = program_parser.split_list(lst, is_char)
        self.assertEqual([[1, 2], [4], [6, 7]], result)

        result2 = program_parser.split_list(lst, is_char, destroy_tokens=False)
        self.assertEqual([['x', 1, 2], ['a', 4], ['b', 6, 7]], result2)


if __name__ == '__main__':
    unittest.main()
