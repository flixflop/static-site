import unittest

from textnode import TextNode
from htmlnode import HTMLNode, LeafNode, ParentNode
from utils import (
	markdown_to_html_node,
	block_to_html_node,
	text_to_children,
	paragraph_to_html_paragraph,
	heading_to_html_heading,
	quote_to_html_quote,
	block_to_block_type,
	ol_to_html_ol,
	ul_to_html_ul,
	markdown_to_blocks,
	text_node_to_html_node, 
	text_to_textnode,
	split_nodes_delimiter, 
	extract_markdown_images, 
	extract_markdown_links, 
	split_nodes_image, 
	split_nodes_link,
	text_type_italic,
	text_type_bold,
	text_type_code,
	text_type_image,
	text_type_link,
	text_type_text
)


class TestTextNode(unittest.TestCase):

	def test_invald_text_node(self):
		inp = TextNode("This is a text node", "invalid")
		with self.assertRaises(ValueError):
			text_node_to_html_node(inp)

	def test_bold_text_node(self):
		inp = TextNode("This is a text node", "bold")
		expected = LeafNode(tag="b", value="This is a text node")
		self.assertEqual(text_node_to_html_node(inp), expected)

	def test_italic_text_node(self):
		inp = TextNode("This is a text node", "italic")
		expected = LeafNode(tag="i", value="This is a text node")
		self.assertEqual(text_node_to_html_node(inp), expected)

	def test_anchor_text_node(self):
		inp = TextNode("This is a text node", "link")
		expected = LeafNode(tag="a", value="This is a text node", props={"href" : None})
		self.assertEqual(text_node_to_html_node(inp), expected)
		inp = TextNode("This is a text node", "link", "www.google.com")
		expected = LeafNode(tag="a", value="This is a text node", props={"href" : "www.google.com"})
		self.assertEqual(text_node_to_html_node(inp), expected)

class TestSplitNodesDelimiter(unittest.TestCase):
	
	def test_spit_nodes_delimiter(self):
		node = TextNode("This is text with a **bolded phrase** in the middle", "text")
		res = split_nodes_delimiter([node], "**", "bold")
		self.assertEqual(len(res), 3)
		self.assertEqual(res[0].text, "This is text with a ")

		node = TextNode("**This is a bolded start** of a text", "text")
		res = split_nodes_delimiter([node], "**", "bold")
		self.assertEqual(len(res), 3)
		self.assertEqual(res[0].text, "")
		self.assertEqual(res[1].text, "This is a bolded start")

		node = TextNode("This is text with a `code` in the middle", "text")	
		res = split_nodes_delimiter([node], "`", "code")
		self.assertEqual(len(res), 3)
		self.assertEqual(res[0].text, "This is text with a ")
		self.assertEqual(res[1].text, "code")

		node = TextNode("This is text with a `code` in the middle and the `end`", "text")	
		res = split_nodes_delimiter([node], "`", "code")
		self.assertEqual(len(res), 5)
		self.assertEqual(res[0].text, "This is text with a ")
		self.assertEqual(res[1].text, "code")
		self.assertEqual(res[-2].text, "end")
		self.assertEqual(res[-2].text_type, "code")
		self.assertEqual(res[-1].text_type, "text")
		self.assertEqual(res[-1].text, "")

		node = TextNode("", "text")
		res = split_nodes_delimiter([node], "**", "bold")
		self.assertEqual(res[0].text, "")

class TestMarkdownExtraction(unittest.TestCase):
	
	def test_extract_markdown_images(self):
		text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
		res = extract_markdown_images(text)
		self.assertEqual(res[0][0], "rick roll")
		self.assertEqual(res, [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")])

		text = "This is a text without images"
		res = extract_markdown_images(text)
		self.assertEqual(res, [])

	def test_extract_markdown_links(self):
		text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
		res = extract_markdown_links(text)
		self.assertEqual(res[0][0], "to boot dev")
		self.assertEqual(res, [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")])

		text = "This is a text without links"
		res = extract_markdown_links(text)
		self.assertEqual(res, [])

class TestMarkdownImageLinkSplitting(unittest.TestCase):

	def test_split_nodes_link(self):
		node = TextNode(
			"This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
			text_type_text,
		)
		new_nodes = split_nodes_link([node])
		self.assertEqual(new_nodes[0].text, "This is text with a link ")
		self.assertEqual(new_nodes[1].text, "to boot dev")
		self.assertEqual(new_nodes[1], TextNode("to boot dev", "link", "https://www.boot.dev"))

		node = TextNode(
			"This is a list of links [to boot dev](https://www.boot.dev), [to youtube](https://www.youtube.com/@bootdotdev)",
			text_type_text,
		)
		new_nodes = split_nodes_link([node])
		self.assertEqual(new_nodes[0].text, "This is a list of links ")
		self.assertEqual(new_nodes[1], TextNode("to boot dev", "link", "https://www.boot.dev"))
		self.assertEqual(new_nodes[2].text, ", ")

		node = TextNode(
			"[to boot dev](https://www.boot.dev)",
			text_type_text,
		)
		new_nodes = split_nodes_link([node])
		self.assertEqual(new_nodes[0].text, "to boot dev")

	def test_split_nodes_image(self):
		node = TextNode(
			"This is text with a link ![to boot dev](https://www.boot.dev) and ![to youtube](https://www.youtube.com/@bootdotdev)",
			text_type_text,
		)
		new_nodes = split_nodes_image([node])
		self.assertEqual(new_nodes[0].text, "This is text with a link ")
		self.assertEqual(new_nodes[1].text, "to boot dev")
		self.assertEqual(new_nodes[1], TextNode("to boot dev", "image", "https://www.boot.dev"))

		node = TextNode(
			"This is a list of links ![to boot dev](https://www.boot.dev), ![to youtube](https://www.youtube.com/@bootdotdev)",
			text_type_text,
		)
		new_nodes = split_nodes_image([node])
		self.assertEqual(new_nodes[0].text, "This is a list of links ")
		self.assertEqual(new_nodes[1], TextNode("to boot dev", "image", "https://www.boot.dev"))
		self.assertEqual(new_nodes[2].text, ", ")

		node = TextNode(
			"![to boot dev](https://www.boot.dev)",
			text_type_text,
		)
		new_nodes = split_nodes_image([node])
		self.assertEqual(new_nodes[0].text, "to boot dev")

class TestTextToTextNode(unittest.TestCase):

	def test_text_to_textnode(self):
		text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
		res = text_to_textnode(text)
		expected = [
			TextNode("This is ", text_type_text),
			TextNode("text", text_type_bold),
			TextNode(" with an ", text_type_text),
			TextNode("italic", text_type_italic),
			TextNode(" word and a ", text_type_text),
			TextNode("code block", text_type_code),
			TextNode(" and an ", text_type_text),
			TextNode("obi wan image", text_type_image, "https://i.imgur.com/fJRm4Vk.jpeg"),
			TextNode(" and a ", text_type_text),
			TextNode("link", text_type_link, "https://boot.dev"),
		]
		self.assertEqual(res, expected)

		text = "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
		res = text_to_textnode(text)

class TestMarkdownToBlocks(unittest.TestCase):

	def test_markdown_to_blocks(self):
		md = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item"""
		
		res = markdown_to_blocks(md)
		self.assertEqual(res[0], "# This is a heading")
		self.assertEqual(res[1], "This is a paragraph of text. It has some **bold** and *italic* words inside of it.")
		self.assertEqual(res[2], "* This is the first list item in a list block\n* This is a list item\n* This is another list item")

		md = " # This is heading with some whitespace. "
		res = markdown_to_blocks(md)
		self.assertEqual(res[0], "# This is heading with some whitespace.")	

		md = """ # This is heading with some whitespace.


Here comes a paragraph but it is separated too far."""
		res = markdown_to_blocks(md)
		self.assertEqual(res[0], "# This is heading with some whitespace.")			
		self.assertEqual(res[1], "Here comes a paragraph but it is separated too far.")

class TestBlockToBlockType(unittest.TestCase):

	def test_block_to_block_type(self):

		for i in range(1, 6):
			md_block = f"{i * '#'} This is a heading"
			res = block_to_block_type(md_block)
			self.assertEqual(res, "heading")
		
		md_block = f"{7 * '#'} This is a heading"
		res = block_to_block_type(md_block)
		self.assertNotEqual(res, "heading")

		md_block = "```\nThis is a code block\n```"
		res = block_to_block_type(md_block)
		self.assertEqual(res, "code")

		md_block = "```This is not a valid code block``"
		res = block_to_block_type(md_block)
		self.assertEqual(res, "paragraph")

		md_block = "> This is a simple quote"
		res = block_to_block_type(md_block)
		self.assertEqual(res, "quote")

		md_block = """* This is list item 1
* This is list item 2
* This is list item 3"""
		res = block_to_block_type(md_block)
		self.assertEqual(res, "unordered_list")

		md_block = """1. This is list item 1
2. This is list item 2
3. This is list item 3"""
		res = block_to_block_type(md_block)
		self.assertEqual(res, "ordered_list")

class TestBlockToHTMLNode(unittest.TestCase):

	def test_text_to_children(self):
		text = "This is some paragraph text which has **bold** and *italic* words."
		res = text_to_children(text)
		self.assertEqual(len(res), 5)
		self.assertEqual(res[0].value, "This is some paragraph text which has ")
		self.assertEqual(res[1].tag, "b")
		self.assertEqual(res[3].tag, "i")

		text = "This is a simple paragraph with no inline elements."
		res = text_to_children(text)
		self.assertEqual(len(res), 1)

	def test_paragraph_to_html_paragraph(self):

		text = "This is a simple paragraph with no inline elements."
		res = paragraph_to_html_paragraph(text)
		self.assertEqual(res.tag, "p")
		self.assertEqual(res.value, "This is a simple paragraph with no inline elements.")
		self.assertEqual(res.children, None)

		text = "This is some paragraph text which has **bold** and *italic* words."
		res = paragraph_to_html_paragraph(text)
		self.assertTrue(isinstance(res, ParentNode))
		self.assertEqual(res.tag, "p")
		self.assertEqual(res.value, None)
		self.assertEqual(len(res.children), 5)

		text = "**I like Tolkien**. Read my [first post here](/majesty) (sorry the link doesn't work yet)"
		res = paragraph_to_html_paragraph(text)
		self.assertEqual(res.tag, "p")

		text = "[some link](link url)"
		text = "![LOTR image artistmonkeys](/images/rivendell.png)"
		res = paragraph_to_html_paragraph(text)
		self.assertEqual(res.tag, "img")

	def test_heading_to_heading_html(self):

		text = "# This is a simple h1 heading."
		res = heading_to_html_heading(text)
		self.assertEqual(res.tag, "h1")
		self.assertEqual(res.value, "This is a simple h1 heading.")
		self.assertEqual(res.children, None)
		self.assertTrue(isinstance(res, LeafNode))

		text = "### This is complex h3 heading with **bold** and *italic* words."
		res = heading_to_html_heading(text)
		self.assertTrue(isinstance(res, ParentNode))
		self.assertEqual(res.tag, "h3")
		self.assertEqual(res.value, None)
		self.assertEqual(len(res.children), 5)

	def test_quote_to_quote_html(self):

		text = "> With great power comes great responsibility."
		res = quote_to_html_quote(text)
		self.assertEqual(res.tag, "blockquote")
		self.assertEqual(res.value, "With great power comes great responsibility.")
		self.assertEqual(res.children, None)
		self.assertTrue(isinstance(res, LeafNode))

		text = "> With great **power** comes great **responsibility**."
		res = quote_to_html_quote(text)
		self.assertEqual(res.tag, "blockquote")
		self.assertEqual(len(res.children), 5)
		self.assertTrue(isinstance(res, ParentNode))

	def test_ul_to_ul_html(self):
		text = """* You can spend years studying the legendarium and still not understand its depths
* It can be enjoyed by children and adults alike
* Disney *didn't ruin it*
* It created an entirely new genre of fantasy"""
		res = ul_to_html_ul(text)



	def test_block_to_html_block(self):
		md = "# This is a cool heading."
		md_type = block_to_block_type(md)
		html = block_to_html_node(md)
		self.assertEqual(md_type, "heading")
		self.assertEqual(html.tag, "h1")
		self.assertEqual(html.value, "This is a cool heading.")

		md = "This is a cool paragraph."
		md_type = block_to_block_type(md)
		html = block_to_html_node(md)
		self.assertEqual(md_type, "paragraph")
		self.assertEqual(html.tag, "p")
		self.assertEqual(html.value, "This is a cool paragraph.")

		md = "This is a more complex paragraph with **bold**, **more bold** and *italic* words."
		md_type = block_to_block_type(md)
		html = block_to_html_node(md)
		self.assertEqual(md_type, "paragraph")
		self.assertEqual(html.tag, "p")
		self.assertTrue(html.children is not None)
		self.assertEqual(html.value, None)
		self.assertEqual(html.children[0].value, "This is a more complex paragraph with ")
		self.assertEqual(len(html.children), 7)
	
		md = """# Tolkien Fan Club

> All that is gold does not glitter

## Reasons I like Tolkien

He create an entirely new way of how to write fantasy.
A few of his inventions are:

* An antihero
* A hero which is not really a hero

## My favorite characters (in order)

1. Gandalf
2. Bilbo
3. Sam
4. Glorfindel
5. Galadriel
6. Elrond
7. Thorin
8. Sauron
9. Aragorn
"""

		md = """# The Unparalleled Majesty of "The Lord of the Rings"

[Back Home](/)

![LOTR image artistmonkeys](/images/rivendell.png)

> "I cordially dislike allegory in all its manifestations, and always have done so since I grew old and wary enough to detect its presence.
> I much prefer history, true or feigned, with its varied applicability to the thought and experience of readers.
> I think that many confuse 'applicability' with 'allegory'; but the one resides in the freedom of the reader, and the other in the purposed domination of the author."

In the annals of fantasy literature and the broader realm of creative world-building, few sagas can rival the intricate tapestry woven by J.R.R. Tolkien in *The Lord of the Rings*. You can find the [wiki here](https://lotr.fandom.com/wiki/Main_Page).

## Introduction

This series, a cornerstone of what I, in my many years as an **Archmage**, have come to recognize as the pinnacle of imaginative creation, stands unrivaled in its depth, complexity, and the sheer scope of its *legendarium*. As we embark on this exploration, let us delve into the reasons why this monumental work is celebrated as the finest in the world.

## A Rich Tapestry of Lore

One cannot simply discuss *The Lord of the Rings* without acknowledging the bedrock upon which it stands: **The Silmarillion**. This compendium of mythopoeic tales sets the stage for Middle-earth's history, from the creation myth of Eä to the epic sagas of the Elder Days. It is a testament to Tolkien's unparalleled skill as a linguist and myth-maker, crafting:

1. [ ] An elaborate pantheon of deities (the `Valar` and `Maiar`)
2. [ ] The tragic saga of the Noldor Elves
3. [ ] The rise and fall of great kingdoms such as Gondolin and Númenor

```
print("Lord")
print("of")
print("the")
print("Rings")
```

## The Art of **World-Building**

### Crafting Middle-earth

Tolkien's Middle-earth is a realm of breathtaking diversity and realism, brought to life by his meticulous attention to detail. This world is characterized by:

- **Diverse Cultures and Languages**: Each race, from the noble Elves to the sturdy Dwarves, is endowed with its own rich history, customs, and language. Tolkien, leveraging his expertise in philology, constructed languages such as Quenya and Sindarin, each with its own grammar and lexicon.
- **Geographical Realism**: The landscape of Middle-earth, from the Shire's pastoral hills to the shadowy depths of Mordor, is depicted with such vividness that it feels as tangible as our own world.
- **Historical Depth**: The legendarium is imbued with a sense of history, with ruins, artifacts, and lore that hint at bygone eras, giving the world a lived-in, authentic feel.
"""

		html_node = markdown_to_html_node(md)
		html_node.to_html()

if __name__ == "__main__":
	unittest.main()