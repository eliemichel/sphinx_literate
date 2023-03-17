from typing import List, Dict
from dataclasses import dataclass
import random

from .registry import CodeBlock

#############################################################
# Parse Backend

Uid = str

@dataclass
class ParsedBlockContent:
    """
    The content of each literate block is parsed and references are replaced
    with unique ids (hashcode) so that they can be recognized after syntax
    highlight is added.
    """

    # Content of teh block where references are replaced with uids
    content: List[str]

    # Holds the mapping from the uids and the original references to other
    # literate code blocks.
    uid_to_block_key: Dict[Uid,str]

#############################################################

def generate_uid() -> Uid:
    return "_" + "".join([random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(32)])

#############################################################

def parse_block_content(content: List[str], tangle_root: str | None, config) -> ParsedBlockContent:
    """
    This reads the raw source code and extracts {{references}} to other blocks,
    not to disturb the syntax highlighter.

    @note At this stage we do not check whether block names exist.

    @param original source code with literate references
    @param tangle_root context of the block
    @param config sphinx config
    @return a parsed block object
    """
    parsed = ParsedBlockContent(
        content = [],
        uid_to_block_key = {},
    )

    raw_source = '\n'.join(content)

    begin_ref = config.lit_begin_ref
    end_ref = config.lit_end_ref

    offset = 0
    parsed_source = ""
    while True:
        begin_offset = raw_source.find(begin_ref, offset)
        if begin_offset == -1:
            break
        end_offset = raw_source.find(end_ref, begin_offset)
        if end_offset == -1:
            print(f"Warning: Found a reference openning '{begin_ref}' but reached end of block before finding the reference closing '{end_ref}'")
            break
        uid = generate_uid()
        block_name = raw_source[begin_offset+len(begin_ref):end_offset]
        parsed.uid_to_block_key[uid] = CodeBlock.build_key(block_name, tangle_root)
        parsed_source += raw_source[offset:begin_offset]
        parsed_source += uid
        offset = end_offset + len(end_ref)

    parsed_source += raw_source[offset:]

    parsed.content = parsed_source.split('\n')

    return parsed

#############################################################
