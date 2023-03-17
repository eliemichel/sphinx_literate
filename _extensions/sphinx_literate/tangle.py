from typing import List

from .registry import CodeBlock, CodeBlockRegistry

#############################################################
# Private

def _tangle_rec(
    lit: CodeBlock,
    registry: CodeBlockRegistry,
    begin_ref: str, # config
    end_ref: str, # config
    tangled_content, # return list
    prefix="" # for recursive use only
) -> None:
    for line in lit.content:
        subprefix = None
        name = None
        begin_offset = line.find(begin_ref)
        if begin_offset != -1:
            end_offset = line.find(end_ref, begin_offset)
            if end_offset != -1:
                subprefix = line[:begin_offset]
                name = line[begin_offset+len(begin_ref):end_offset]
        if name is not None:
            sublit = registry.get(name, lit.tangle_root)
            if lit is None:
                message = (
                    f"Literate code block not found: '{name}' " +
                    f"(in tangle directive from document {lit.docname}, " +
                    f"line {lit.lineno}, tangle root {lit.tangle_root})"
                )
                raise ExtensionError(message, modname="sphinx_literate")
            _tangle_rec(
                sublit,
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
    block_name: str,
    tangle_root: str | None,
    lit_codeblocks: CodeBlockRegistry,
    config # sphinx app config
) -> List[str]:
    """
    Tangle a given code block, i.e. resolve all the references to generate a
    full code without any more pending reference in it.
    @param block_name the name of the block to tangle
    @param tangle_root the name of the root directory: two code blocks with the
           same name may exist only if they belong to different root directories.
    @param lit_codeblocks the registry containing all the code blocks extracted
           from the source documentation.
    @return the generated source code as a list of lines
    """
    lit = lit_codeblocks.get(block_name, tangle_root)
    if lit is None:
        message = (
            f"Literate code block not found: '{block_name}' " +
            f"(tangle root {tangle_root})"
        )
        raise ExtensionError(message, modname="sphinx_literate")

    tangled_content = []
    _tangle_rec(
        lit,
        lit_codeblocks,
        config.lit_begin_ref,
        config.lit_end_ref,
        tangled_content,
    )
    return tangled_content
