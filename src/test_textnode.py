import unittest

from textnode import TextNode


class TestTextNode(unittest.TestCase):
	def test_eq(self):
		node = TextNode("This is a text node", "bold")
		node2 = TextNode("This is a text node", "bold")
		self.assertEqual(node, node2)

	def test_node_uneq(self):
		node = TextNode("This is a text node", "bold", "https://random.url.io")
		node2 = TextNode("This is a text node", "bold")
		self.assertNotEqual(node, node2)

	def test_uneq(self):
		node = TextNode("This is a text node", "bold")
		node2 = TextNode("This is a text node", "italics")
		self.assertNotEqual(node, node2)

	def test_repr(self):
		node = TextNode("This is a text node", "bold")
		self.assertEqual(str(node), f"TextNode(This is a text node, bold, None)")

	def test_url(self):
		node = TextNode("This is a text node", "bold")
		self.assertEqual(node.url, None)
		node = TextNode("This is a bold text.", "bold", "https://random.url.io")
		self.assertEqual(node.url, "https://random.url.io")


if __name__ == "__main__":
	unittest.main()