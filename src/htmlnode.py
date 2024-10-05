class HTMLNode:

	def __init__(self, tag: str=None, value: str=None, children: list=None, props: dict=None):
		self.tag = tag
		self.value = value
		self.children = children
		self.props = props

	def to_html(self):
		raise NotImplementedError
	
	def props_to_html(self) -> str:
		html_str = ""
		if self.props:
			for key in self.props:
				sub_string = f" {key}=\"{self.props[key]}\""
				html_str += sub_string
			return html_str
		return html_str
	
	def __repr__(self) -> str:
		return f"HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"
	
	def __eq__(self, other: object) -> bool:
		return (self.tag, self.value, self.children, self.props) == (other.tag, other.value, other.children, other.props)
	
class LeafNode(HTMLNode):

	def __init__(self, tag: str, value: str, props: dict=None):
		super().__init__(tag=tag, value=value, props=props)

	def to_html(self):
		if self.value is None:	
			raise ValueError("A LeafNode must have a value")
		
		if self.tag is None:
			return self.value
		
		return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
	
class ParentNode(HTMLNode):

	def __init__(self, tag: str, children: list, props: dict=None):
		super().__init__(tag=tag, children=children, props=props)


	def to_html(self):
		if self.tag is None:
			raise ValueError("Parentnode needs a tag.")
		
		if self.children is None or self.children == []:
			raise ValueError("ParentNode must have children.")
		
		child_str = ""
		for child in self.children:
			#if child:
			child_str += child.to_html()
		
		return f"<{self.tag}{self.props_to_html()}>{child_str}</{self.tag}>"