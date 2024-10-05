import unittest

from main import extract_title

class TestExtractTitle(unittest.TestCase):

	def test_extract_title(self):
		md = "# This is a title!"
		res = extract_title(md)
		self.assertEqual(res, "This is a title!")

		with self.assertRaises(ValueError):
			extract_title("## This is not an h1 title!")