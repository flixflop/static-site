import re

from htmlnode import LeafNode, ParentNode, HTMLNode
from textnode import TextNode

text_type_text = "text"
text_type_bold = "bold"
text_type_code = "code"
text_type_italic = "italic"
text_type_image = "image"
text_type_link = "link"

### TextNode to HTMLNode
def text_node_to_html_node(text_node : TextNode) -> LeafNode:
	"""
	Takes a TextNode and turns it into an HTMLNode.

	:params:
	text_node: TextNode

	:return:
	HTMLNode
	"""
	valid_text_to_html = {
		"text" : LeafNode(tag=None, value=text_node.text), 
		"bold" : LeafNode(tag="b", value=text_node.text),
		"italic" : LeafNode(tag="i", value=text_node.text),
		"code" : LeafNode(tag="code", value=text_node.text),
		"link" : LeafNode(tag="a", value=text_node.text, props={"href" : text_node.url}),
		"image" : LeafNode(
			tag="img", 
			value=text_node.text, 
			props={"src" : text_node.url, "alt" : text_node.text})
	}
	if text_node.text_type in valid_text_to_html:
		return valid_text_to_html[text_node.text_type]
		
	raise ValueError("TextNode does not contain a valid text_type")

### Markdown 
def markdown_to_html_node(markdown: str) -> ParentNode:
	children = []
	# split markdown into blocks
	md_blocks = markdown_to_blocks(markdown)

	# loop over blocks
	for md_block in md_blocks:
		html_node = block_to_html_node(md_block)
		children.append(html_node)
		
	return ParentNode(tag="div", children=children)

def block_to_html_node(markdown_block: str) -> HTMLNode:
	"""
	This helper function is supposed to take in a 
	markdown block, e.g. a heading, and return the correct
	HTMLNode representation.
	
	Caveats:
	- We need to know if our element is a ParentNode or LeafNode:
	  - heading: is probably a LeafNode because it only has a value and no children 
	  - paragraph: may contain inline elements and then is a ParentNode, but if there are no inline elements --> LeafNode
	  - quote: probably a LeafNode?! Or could there be inline HTML in a blockquote --> ParentNode
	  - ordered_list: Should be a parent because it contains list items --> List Items are probably leaves because they only contain text.
	  - unoredered_list: similar to ordered list
	  - code: could be similar to quote

	To cover those caveats we should be able to use the text_to_children function below
	"""
	func_dict = {
		"heading" : heading_to_html_heading,
		"paragraph" : paragraph_to_html_paragraph,
		"code" : code_to_html_code,
		"quote" : quote_to_html_quote,
		"ordered_list" : ol_to_html_ol,
		"unordered_list" : ul_to_html_ul
	}
	block_type = block_to_block_type(markdown_block)
	return func_dict[block_type](markdown_block)

def heading_to_html_heading(markdown_heading: str):

	heading_level, heading_text = markdown_heading.split(" ", 1)
	tag = f"h{len(heading_level)}"
	children = text_to_children(heading_text)
	if len(children) > 1:
		return ParentNode(tag=tag, children=children)
	return LeafNode(tag=tag, value=heading_text)

def paragraph_to_html_paragraph(markdown_paragraph: str):
	tag = "p"
	children = text_to_children(markdown_paragraph)
	if len(children) > 1:
		return ParentNode(tag=tag, children=children)
	if len(children) == 1 and children[0].tag:
		return ParentNode(tag=tag, children=children)
	return LeafNode(tag=tag, value=markdown_paragraph)

def quote_to_html_quote(markdown_quote: str):
	tag = "blockquote"
	_, quote_text = markdown_quote.split("> ", 1)
	children = text_to_children(markdown_quote)
	if len(children) > 1:
		return ParentNode(tag=tag, children=children)
	return LeafNode(tag=tag, value=quote_text)
	
	

def code_to_html_code(markdown_code: str):
	tag = "code"
	children = text_to_children(markdown_code)
	if not children:
		return ParentNode(tag="pre", children=[LeafNode(tag=tag, value=text_node_to_html_node(markdown_code))])
	return ParentNode(tag="pre", children=[ParentNode(tag=tag, children=children)])

def ul_to_html_ul(markdown_ul: str):
	tag = "li"
	ul_node = ParentNode(tag="ul", children=[])
	# Split list along new line characters
	for item in markdown_ul.split("\n"):
		try:
			_, item_text = item.split("* ", 1)
		except:
			try:
				_, item_text = item.split("- ", 1)
			except:
				return
		item_text_node = text_to_children(item_text)
		ul_node.children.append(ParentNode(tag=tag, children=item_text_node))
	return ul_node

def ol_to_html_ol(markdown_ol: str):
	tag = "li"
	ol_node = ParentNode(tag="ol", children=[])
	# Split list along new line characters
	for item in markdown_ol.split("\n"):
		_, item_text = item.split(". ", 1)
		item_text_node = text_to_children(item_text)
		ol_node.children.append(ParentNode(tag=tag, children=item_text_node))
	return ol_node

def text_to_children(text):
	"""
	This should turn markdown text into the correct HTMLNodes.
	We can probably reuse the text_node_to_html_node code written previously.
	But for this to work, we first have to transform the text into a TextNode
	"""	
	text_nodes = text_to_textnode(text)
	return [text_node_to_html_node(text_node) for text_node in text_nodes]	

def block_to_block_type(markdown_block: str) -> str:

	# In case of quotes or lists
	lines = markdown_block.split("\n")
	# For headings, only first_line should exist.
	first_line = lines[0]

	if first_line.startswith("#"):
		parts = first_line.split(" ", 1)
		if len(parts) == 2 and 1 <= len(parts[0]) <= 6 and all(char == "#" for char in parts[0]):
			return "heading"
		
	if len(lines) >= 2 and lines[0].strip() == "```" and lines[-1].strip() == "```":
		return "code"
	
	if all(line.startswith(">") or line == "" for line in lines):
		return "quote"
	
	if all(line.startswith("* ") or line.startswith("- ") or line == "" for line in lines):
		return "unordered_list"
	
	def is_ordered_list(lines: list[str]) -> bool:
		if not lines:
			return False
		
		first_line = lines[0]
		parts = first_line.split(". ", 1)
		if len(parts) != 2:
			return False

		try:
			start_num = int(parts[0])
		except ValueError:
			return False	

		for i, line in enumerate(lines, start=start_num):
			if not line.startswith(f"{i}. "):
				return False
		return True
			
	if is_ordered_list(lines):
		return "ordered_list"
			
	return "paragraph"

def markdown_to_blocks(markdown: str) -> list[str]:
	"""
	Takes a string of raw markdown and turns it into a list of
	block-levle strings.
	We assume that each block is separated by a blank line.

	parameters:
	* markdown: a string of raw markdown

	return:
	* list of block-level markdown strings

	Example:
	# This is a heading

	This is a paragraph of text. It has some **bold** and *italic* words inside of it.

	* This is the first list item in a list block
	* This is a list item
	* This is another list item

	[
		"# This is a heading",
		"This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
		"* This is the first list item in a list block
		* This is a list item
		* This is another list item
		"
	]
	"""
	block_markdown = []
	split_markdown = markdown.split("\n\n")
	for block in split_markdown:
		if block != "":
			block_markdown.append(block.strip())
	
	return block_markdown


### Inline text to TextNode
def text_to_textnode(text: str) -> list[TextNode]:
    text_node = TextNode(text=text, text_type=text_type_text)
    img = split_nodes_image([text_node])
    lnk = split_nodes_link(img)
    bold = split_nodes_delimiter(lnk, "**", text_type_bold)
    italic = split_nodes_delimiter(bold, "*", text_type_italic)
    code = split_nodes_delimiter(italic, "`", text_type_code)
    return code

### Text splitting
def split_nodes_delimiter(
		old_nodes: list[TextNode],
		delimiter: str, 
		text_type: str) -> list[TextNode]:
	"""
	new_nodes_delimiter takes a list of TextNodes, a specified
	delimiter and a text_type and returns a new list
	of TextNodes where each TextNode of type text is split into
	new TextNodes.

	Example:

	"This is text with a **bolded phrase** in the middle"

	Should become
	[
		TextNode("This is text with a ", "text"),
		TextNode("bolded phrase", "bold"),
		TextNode(" in the middle", "text"),
	]

	"""
	new_nodes = []

	for node in old_nodes:
		if node.text_type != text_type_text:
			new_nodes.append(node)
			continue

		parts = node.text.split(delimiter)
		if len(parts) % 2 == 0:
			raise Exception(f"Invalid markdown: Unmatched delimiter {delimiter}")
		
		current_type = text_type_text
		for part in parts:
			new_nodes.append(TextNode(part, current_type))
			current_type = text_type if current_type == text_type_text else text_type_text

	return new_nodes

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
	new_nodes = []

	for node in old_nodes:
		if node.text_type != text_type_text:
			new_nodes.append(node)
			continue

		images = extract_markdown_images(node.text)
		if not images:
			new_nodes.append(node)
			continue

		current_position = 0

		for i, image in enumerate(images):
			markup = f"![{image[0]}]({image[1]})"
			image_position = node.text.find(markup, current_position)

			# Extract text up to the current link
			before_image = node.text[current_position:image_position]
			after_image = node.text[image_position+len(markup):]
			if before_image:
				new_nodes.append(TextNode(before_image, text_type_text))

			# Add the link node
			new_nodes.append(TextNode(image[0], text_type_image, image[1]))

			if i == len(images)-1 and after_image:
				new_nodes.append(TextNode(after_image, text_type_text))


			# Move the current position past the link markup
			if image_position + len(markup) < len(node.text):
				if node.text[image_position + len(markup)] == " ":
					current_position = image_position + len(markup) + 1
				else:
					current_position = image_position + len(markup)

	return new_nodes

def extract_markdown_images(text: str) -> list[tuple]:
	"""
	extract_markdown_images extracts the image url and image alt text
	from a markdown string.

	Example:
	text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
	print(extract_markdown_images(text))
	# [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
	"""
	return re.findall(r"!\[(.*?)\]\((.*?)\)", text)

# def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
# 	"""
# 	Example:
# 	node = TextNode(
#     	"This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
#     	text_type_text,
# 	)
# 	new_nodes = split_nodes_link([node])
# 	# [
# 	#     TextNode("This is text with a link ", text_type_text),
# 	#     TextNode("to boot dev", text_type_link, "https://www.boot.dev"),
# 	#     TextNode(" and ", text_type_text),
# 	#     TextNode(
# 	#         "to youtube", text_type_link, "https://www.youtube.com/@bootdotdev"
# 	#     ),
# 	# ]
# 	"""
# 	new_nodes = []

# 	for node in old_nodes:
# 		if node.text_type != text_type_text:
# 			new_nodes.append(node)
# 			continue

# 		links = extract_markdown_links(node.text)
# 		if not links:
# 			if node.text != "":
# 				new_nodes.append(node)
# 			continue

# 		md_link = f"[{links[0][0]}]({links[0][1]})"
# 		parts = node.text.split(md_link)
# 		new_nodes.extend(
# 			[
# 				TextNode(parts[0], text_type_text),
# 				TextNode(links[0][0], text_type_link, links[0][1]),
# 			]
# 		)
# 		new_nodes.extend(split_nodes_link([TextNode(parts[1], text_type_text)]))

# 	return new_nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
	"""
	Example:
	node = TextNode(
		"This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
		text_type_text,
	)
	new_nodes = split_nodes_link([node])
	# [
	#     TextNode("This is text with a link ", text_type_text),
	#     TextNode("to boot dev", text_type_link, "https://www.boot.dev"),
	#     TextNode(" and ", text_type_text),
	#     TextNode(
	#         "to youtube", text_type_link, "https://www.youtube.com/@bootdotdev"
	#     ),
	# ]
	"""
	new_nodes = []

	for node in old_nodes:
		if node.text_type != text_type_text:
			new_nodes.append(node)
			continue

		links = extract_markdown_links(node.text)
		if not links:
			new_nodes.append(node)
			continue
		current_position = 0

		for i, link in enumerate(links):
			markup = f"[{link[0]}]({link[1]})"
			link_position = node.text.find(markup, current_position)

			# Extract text up to the current link
			before_link = node.text[current_position:link_position]
			after_link = node.text[link_position+len(markup):]
			if before_link:
				new_nodes.append(TextNode(before_link, text_type_text))

			# Add the link node
			new_nodes.append(TextNode(link[0], text_type_link, link[1]))

			if i == len(links)-1 and after_link:
				new_nodes.append(TextNode(after_link, text_type_text))

			# Move the current position past the link markup
			if link_position + len(markup) < len(node.text):
				if node.text[link_position + len(markup)] == " ":
					current_position = link_position + len(markup) + 1
				else:
					current_position = link_position + len(markup)

	return new_nodes




def extract_markdown_links(text: str) -> list[tuple]:
	"""
	extract_markdown_links extracts the link and its name from 
	a markdown string.

	text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
	print(extract_markdown_links(text))
	# [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
	"""
	return re.findall(r"\[(.*?)\]\((.*?)\)", text)
