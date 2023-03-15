from typing import List

from .registry import CodeBlockRegistry

#############################################################
# Private

def _tangle_rec(
    lit_content: List[str],
    registry: CodeBlockRegistry,
    begin_ref: str, # config
    end_ref: str, # config
    tangled_content, # return list
    prefix="" # for recursive use only
) -> None:
    for line in lit_content:
        subprefix = None
        key = None
        begin_offset = line.find(begin_ref)
        if begin_offset != -1:
            end_offset = line.find(end_ref, begin_offset)
            if end_offset != -1:
                subprefix = line[:begin_offset]
                key = line[begin_offset+len(begin_ref):end_offset]
        if key is not None:
            sublit = registry.get(key)
            if sublit is None:
                message = (
                    f"Literate code block not found: '{key}' " +
                    f"(in tangle directive from document {node.docname}, line {node.lineno})"
                )
                raise ExtensionError(message, modname="sphinx_literate")
            _tangle_rec(
                sublit.content,
                registry,
                begin_ref,
                end_ref,
                tangled_content,
                prefix=prefix + subprefix
            )
        else:
            tangled_content.append(prefix + line)

#############################################################
# Public

def tangle(
    lit_block_key: str,
    lit_codeblocks: CodeBlockRegistry,
    config # sphinx app config
) -> List[str]:
    tangled_content = []
    _tangle_rec(
        lit_codeblocks.get(lit_block_key).content,
        lit_codeblocks,
        config.lit_begin_ref,
        config.lit_end_ref,
        tangled_content,
    )
    return tangled_content
