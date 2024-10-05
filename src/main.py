import os
import shutil
from textnode import TextNode
from utils import markdown_to_blocks, block_to_block_type, markdown_to_html_node

def copy_tree(src: str, dst: str):
	"""
	Copy an entire directory tree.

	parameters:
	:src: A relative path from the root of the project.
	:dst: A relative path from the root of the project.
	"""
	root = os.path.abspath(".")
	if not os.path.exists(os.path.join(root, dst)):
		os.mkdir(os.path.join(root, dst))
	for item in os.listdir(os.path.join(root, src)):
		src_path = os.path.join(root, f"{src}/{item}")
		dst_path = os.path.join(root, f"{dst}/{item}")

		if not os.path.isfile(src_path):
			os.mkdir(dst_path)
			print(f"Directory {dst_path} created")
			copy_tree(f"{src}/{item}", f"{dst}/{item}")
		else:
			shutil.copy(src_path, dst_path)
			print(f"Flie {src_path} copied to {dst_path}")


def remove_tree(dst: str):
	"""
	Remove an entire directory tree.
	"""
	root = os.path.abspath(".")
	dst = os.path.join(root, dst)
	if os.path.exists(dst):
		shutil.rmtree(dst)
	else:
		print("Directory {dst} does not exist. Nothing to delete!")

def extract_title(markdown):
	md_blocks = markdown_to_blocks(markdown)
	for md_block in md_blocks:
		if block_to_block_type(md_block) == "heading" and "#" not in md_block.split("# ", 1):
			_, heading_text = md_block.split("# ", 1)
			return heading_text
		raise ValueError("No h1 heading could be found!")
	
def generate_page_recursive(dir_path_content, template_path, dest_dir_path):

	root = os.path.abspath(".")
	dir_path = os.path.join(root, dir_path_content)
	dst_path = os.path.join(root, dest_dir_path)
	for item in os.listdir(dir_path):
		if not os.path.isfile(os.path.join(dir_path, item)):
			if not os.path.exists(os.path.join(dst_path, item)):
				os.mkdir(os.path.join(dst_path, item))
			generate_page_recursive(
				dir_path_content=os.path.join(dir_path, item),
				template_path=template_path,
				dest_dir_path=os.path.join(dst_path, item)
			)
		else:
			generate_page(
				from_path=os.path.join(dir_path, item),
				template_path=template_path,
				dest_path=os.path.join(dst_path, item)
				)

def generate_page(from_path, template_path, dest_path):
	print(f"{30 * '#'}")
	print(f"Generating page from {from_path} to {dest_path} using {template_path}")
	print(f"{30 * '#'}")

	with open(from_path, "r") as f:
		md = f.read()

	with open(template_path, "r") as f:
		tmpl = f.read()
	
	title = extract_title(md)
	node = markdown_to_html_node(md)
	html = node.to_html()

	tmpl = tmpl.replace("{{ Title }}", title)
	tmpl = tmpl.replace("{{ Content }}", html)

	path, file_name = os.path.split(dest_path)
	file_name = file_name.split(".", 1)[0] + ".html"
	dest_path = os.path.join(path, file_name)
	with open(dest_path, "w") as f:
		f.write(tmpl)




def main():
	import time
	remove_tree(dst="public")
	copy_tree(src="static", dst="public")
	root = os.path.abspath(".")
	generate_page_recursive(
		dir_path_content="content",
		dest_dir_path="public",
		template_path="template.html"
	)

if __name__ == "__main__":
	main()