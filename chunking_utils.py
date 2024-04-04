import bs4
import tiktoken
import re
import tree_sitter_languages

from typing import Any, List

parser = tree_sitter_languages.get_parser("python")
MAX_CHARS =1500

def num_tokens(input: str, encoding: tiktoken.core.Encoding) -> int:
    return len(encoding.encode(input))

# design choice: Assume that only natural language is being cleaned and split using this function. Assume that all code
#                is inside <pre> preformatted tags and will be handled differently by chunk function
def clean_and_split_text_input(input: str, max_chunk_size_tokens: int, encoding: tiktoken.core.Encoding) -> list[str]:
    # assuption: there wont be anny monster sentances longer than the max chunk size in tokens
    sentances = re.split(r'(?<=\.|\?|\!)\s', input)
    # this to also stripw tabs and runs of more than one space
    sentances = [re.sub("\s+", " ", sentance).strip() for sentance in sentances]
    # ToDo: add a filter here to remove all empty sentances instead of checking for them in the for loop
    output = list()
    sentance_buffer = ""
    for sentance in sentances:
        if sentance == "":
            continue
        if num_tokens(sentance_buffer + " " + sentance, encoding) <= max_chunk_size_tokens:
            sentance_buffer += (" " if len(sentance_buffer) > 0 else "") + sentance
        else:
            output.append(sentance_buffer)
            sentance_buffer = sentance
    if len(sentance_buffer) > 0:
        output.append(sentance_buffer)
    return output

# assume all preformatted text is python code
def chunk_code_text(text: str):
    tree = parser.parse(bytes(text, "utf-8"))
    return _chunk_node(tree.root_node, text)


def _chunk_node(node: Any, text: str, last_end: int = 0) -> List[str]:
    new_chunks = []
    current_chunk = ""
    for child in node.children:
        if child.end_byte - child.start_byte > MAX_CHARS:
            # Child is too big, recursively chunk the child
            child_chunks = _chunk_node(child, text, last_end)
            if len(child_chunks) == 0:
                print("=====weird child chunk indexing error=====")
                continue
            if len(current_chunk) == 0:
                new_chunks.extend(child_chunks)
            elif len(current_chunk) + len(child_chunks[0])  + len("\n") < MAX_CHARS:
                new_chunks.append(current_chunk + "\n" + child_chunks[0])
                new_chunks.extend(child_chunks[1:])
            else:
                new_chunks.append(current_chunk)
                new_chunks.extend(child_chunks)
            current_chunk = ""
        elif (
            len(current_chunk) + child.end_byte - child.start_byte > MAX_CHARS
        ):
            # Child would make the current chunk too big, so start a new chunk
            new_chunks.append(current_chunk)
            current_chunk = text[last_end : child.end_byte]
        else:
            current_chunk += text[last_end : child.end_byte]
        last_end = child.end_byte
    if len(current_chunk) > 0:
        new_chunks.append(current_chunk)
    return new_chunks


# takes a bs5 Tag as an argument and returns the chunked text from all the
# descendents of that tag
# calls itself recursively working down the HTML tree structure
# Merges segments of text into chunks no greater than max chunk size
# biased toward merging text from sibling-elements over merging text from cousin-elements
# recursively merges chunks of text up the tree
def chunk(tag : bs4.element.Tag, max_chunk_size_tokens: int, encoding: tiktoken.core.Encoding) -> list[str]:
    # ToDo: I think this type hint syntax is wrong but python is too much of an interpreted language
    # to give me an error
    chunks : list[str]= list()
    for child_tag in tag.children:
        # treat preformatted text tags different from other tags so they retain their formatting etc
        if child_tag.name == "pre":
            preformatted_text = child_tag.get_text()
            chunked_code = chunk_code_text(preformatted_text)
            # ToDo: add some logic for dealing with preformatted text segments that are longer than the max token chunk size
            if len(chunks) > 0 and num_tokens("\n" + chunked_code[0], encoding) + num_tokens(chunks[-1], encoding) <= max_chunk_size_tokens:
                chunks[-1] = chunks[-1] + "\n" + chunked_code[0]
                chunks.extend(chunked_code[1:])
            else:
                chunks.extend(chunked_code)
            
        elif child_tag.string:
            temp = clean_and_split_text_input(str(child_tag.string), max_chunk_size_tokens, encoding)
            if len(temp) == 0:
                continue
            if len(chunks) > 0 and num_tokens(chunks[-1], encoding) + num_tokens(" " + temp[0], encoding) <= max_chunk_size_tokens:
                chunks[-1] = chunks[-1] + " " + temp[0]
                chunks.extend(temp[1:])
            else:
                chunks.extend(temp)
        else:
            # this is meant to mean the nephew tag to the chunk currently in the end of the chunk array
            child_child_tag_chunks = chunk(tag=child_tag, max_chunk_size_tokens=max_chunk_size_tokens, encoding=encoding)
            if len(chunks) > 0 and len(child_child_tag_chunks) > 0 and \
                num_tokens(chunks[-1], encoding) + num_tokens(child_child_tag_chunks[0], encoding) <= max_chunk_size_tokens:
                chunks[-1] = chunks[-1] + " " + child_child_tag_chunks[0]
                chunks.extend(child_child_tag_chunks[1:])
            else:
                chunks.extend(child_child_tag_chunks)
    return chunks