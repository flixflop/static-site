import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):

	def test_repr(self):
		node = HTMLNode(tag="a", value=None, children=[], props={"href" : "www.google.com"})
		expected_str = "HTMLNode(tag=a, value=None, children=[], props={'href': 'www.google.com'})"
		self.assertEqual(str(node), expected_str) 

	def test_props_to_html(self):
		node = HTMLNode(tag="a", value=None, children=[], props={"href" : "www.google.com"})
		prop_str = node.props_to_html()
		self.assertEqual(prop_str, ' href="www.google.com"')

	def test_props_to_html(self):
		node = HTMLNode(tag="a", value=None, children=[], props={"href" : "www.google.com", "target" : "_blank"})
		prop_str = node.props_to_html()
		self.assertEqual(prop_str, ' href="www.google.com" target="_blank"')

class TestLeafNode(unittest.TestCase):

	def test_missing_value(self):
		node = LeafNode(tag="a", value=None, props={"href" : "www.google.com"})
		with self.assertRaises(ValueError):
			node.to_html()

	def test_missing_tag_missing_value(self):
		node = LeafNode(tag=None, value=None, props={"href" : "www.google.com"})
		with self.assertRaises(ValueError):
			node.to_html()

	def test_missing_tag_missing(self):
		node = LeafNode(tag=None, value="Some cool value", props={"href" : "www.google.com"})
		self.assertEqual("Some cool value", node.to_html())

	def test_to_html_with_props(self):
		node = LeafNode(tag="a", value="Some cool value", props={"href" : "www.google.com"})
		self.assertEqual(node.to_html(), '<a href="www.google.com">Some cool value</a>')
	
	def test_to_html_without_props(self):
		node = LeafNode(tag="p", value="Some cool value", props=None)
		self.assertEqual(node.to_html(), '<p>Some cool value</p>')

class TestParentNode(unittest.TestCase):

	def test_missing_tag(self):
		node = ParentNode(
			None,
			[
				LeafNode("b", "Bold text"),
				LeafNode(None, "Normal text"),
				LeafNode("i", "italic text"),
				LeafNode(None, "Normal text"),
			]
		)
		with self.assertRaises(ValueError):
			node.to_html()

	def test_missing_children(self):
		node = ParentNode(
			None,
			None
		)
		with self.assertRaises(ValueError):
			node.to_html()

	def test_missing_children_empty_list(self):
		node = ParentNode(
			"p",
			[]
		)
		with self.assertRaises(ValueError):
			node.to_html()

	def test_parent_children_to_html(self):
		node = ParentNode(
			"p",
			[
				LeafNode("b", "Bold text"),
				LeafNode(None, "Normal text"),
				LeafNode("i", "italic text"),
				LeafNode(None, "Normal text"),
			],
		)

		self.assertEqual(
			node.to_html(),
			"<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
		)

	def test_complex_parent_children_to_html(self):
		node = ParentNode(
			"h1",
			[
				ParentNode(
				"p",
					[
						LeafNode("b", "Bold text"),
						LeafNode(None, "Normal text"),
						LeafNode("i", "italic text"),
						LeafNode(None, "Normal text"),
					],
				),
			
				ParentNode(
					"h2",
					[
						LeafNode("b", "Bold text"),
						LeafNode(None, "Normal text"),
						LeafNode("i", "italic text"),
						LeafNode(None, "Normal text"),
					],
				)
			]	
		)

		self.assertEqual(
			node.to_html(),
			"<h1><p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p><h2><b>Bold text</b>Normal text<i>italic text</i>Normal text</h2></h1>"
		)

	def test_complex_parent_children_to_html_with_props(self):
		node = ParentNode(
			"h1",
			[
				ParentNode(
				"p",
				[
					LeafNode("b", "Bold text"),
					LeafNode(None, "Normal text"),
					LeafNode("i", "italic text"),
					LeafNode(None, "Normal text"),
				],
				{"class" : "some-cool-css-class"}
				),
			
				ParentNode(
					"h2",
					[
						LeafNode("b", "Bold text"),
						LeafNode(None, "Normal text"),
						LeafNode("i", "italic text"),
						LeafNode(None, "Normal text"),
					],
				)
			]	
		)

		self.assertEqual(
			node.to_html(),
			'<h1><p class="some-cool-css-class"><b>Bold text</b>Normal text<i>italic text</i>Normal text</p><h2><b>Bold text</b>Normal text<i>italic text</i>Normal text</h2></h1>'
		)
		
	