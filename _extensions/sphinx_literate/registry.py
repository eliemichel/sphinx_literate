from __future__ import annotations
from typing import Any
from dataclasses import dataclass

from sphinx.errors import ExtensionError

#############################################################
# Codeblock

@dataclass
class CodeBlock:
    """
    Data store about a code block parsed from a {lit} directive, to be
    assembled when tangling.
    """
    name: str = ""

    docname: str = ""

    # tangle_root as defined by lit-setup at the time the block was created
    tangle_root: str | None = ""

    lineno: int = -1

    content: str = ""

    # target anchor for referencing this code block in internal links
    target: Any = None

    lexer: str | None = None

    @property
    def key(self):
        return self.build_key(self.name, self.tangle_root)

    @classmethod
    def build_key(cls, name, tangle_root=None):
        if tangle_root is None:
            tangle_root = ""
        return tangle_root + "##" + name

#############################################################
# Codeblock registry

class CodeBlockRegistry:
    """
    Holds the various code blocks and prevents duplicates.
    NB: Do not create this yourself, call CodeBlockRegistry.from_env(env)
    """

    @classmethod
    def from_env(cls, env) -> CodeBlockRegistry:
        if not hasattr(env, 'lit_codeblocks'):
            env.lit_codeblocks = CodeBlockRegistry()
        return env.lit_codeblocks

    def __init__(self) -> None:
        self._blocks = {}

    def add_codeblock(self, lit: CodeBlock) -> None:
        if "##" in lit.name:
            message = (
                f"The sequence '##' is not allowed in a block name, " +
                f"it is reserved to internal mechanisms.\n"
            )
            raise ExtensionError(message, modname="sphinx_literate")

        key = lit.key
        existing = self._blocks.get(key)
        if existing is not None:
            message = (
                f"Multiple literate code blocks with the same name '{key}' were found:\n" +
                f"  - In document '{existing.docname}', line {existing.lineno}.\n"
                f"  - In document '{lit.docname}', line {lit.lineno}.\n"
            )
            raise ExtensionError(message, modname="sphinx_literate")
        self._blocks[key] = lit

    def remove_codeblocks_by_docname(self, docname: str) -> None:
        self._blocks = {
            key: lit
            for key, lit in self._blocks.items()
            if lit.docname != docname
        }

    def blocks(self) -> CodeBlock:
        return self._blocks.values()

    def get_by_key(self, key: str) -> CodeBlock:
        return self._blocks.get(key)

    def get(self, name: str, tangle_root: str | None = None) -> CodeBlock:
        return self.get_by_key(CodeBlock.build_key(name, tangle_root))

    def keys(self, key: str) -> dict_keys:
        return self._blocks.keys()

    def items(self) -> dict_items:
        return self._blocks.items()
