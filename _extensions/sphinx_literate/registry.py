from __future__ import annotations
from typing import Any, Dict, Set
from dataclasses import dataclass, field
from collections import defaultdict

from sphinx.errors import ExtensionError

#############################################################
# Codeblock

Key = str

@dataclass
class CodeBlock:
    """
    Data store about a code block parsed from a {lit} directive, to be
    assembled when tangling.
    """

    # Name of the code block (see title parsing)
    name: str = ""

    # Source document where the block was defined
    docname: str = ""

    # Tangle root as defined by lit-setup at the time the block was created
    tangle_root: str | None = ""

    # Line number at which the code block was defined in the source document
    lineno: int = -1

    # A list of lines
    content: List[str] = field(default_factory=list)

    # Target anchor for referencing this code block in internal links
    target: Any = None

    lexer: str | None = None

    # NB: Fields bellow are handled by the registry

    # A block has children when it gets appended some content in later blocks
    # (this is a basic doubly linked list)
    next: CodeBlock | None = None
    prev: CodeBlock | None = None

    # The index of the block in the child list
    child_index: int = 0

    @property
    def key(self) -> Key:
        return self.build_key(self.name, self.tangle_root)

    @classmethod
    def build_key(cls, name, tangle_root=None) -> Key:
        if tangle_root is None:
            tangle_root = ""
        return tangle_root + "##" + name

    def all_content(self):
        """
        Iterate on all lines of content, including children
        """
        for l in self.content:
            yield l
        if self.next is not None:
            for l in self.next.all_content():
                yield l

#############################################################

@dataclass
class TangleHierarchyEntry:
    """
    Store options for each tangle root about the first lit-setup directive that
    defiend its parent.
    """
    root: str
    parent: str
    docname: str
    lineno: int

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
        # Literate code blocks that have been define, indexed by their key.
        # If blocks with the same key have been appended, they are accessed
        # using the `next` member of CodeBlock.
        self._blocks: Dict[Key,CodeBlock] = {}

        # Store an index of all the references to a block
        # self._references[key] lists all blocks that reference key
        self._references: Dict[Key,Set[Key]] = defaultdict(set)

        # Holds the relationship between different tangle roots.
        # This maps a root to its parent
        self._hierarchy: Dict[str,TangleHierarchyEntry] = {}

    def add_codeblock(self, lit: CodeBlock) -> None:
        """
        Add a new code block to the repository. If a block already exists with
        the same key, an error is raised.
        @param lit block to add
        """
        if "##" in lit.name:
            message = (
                f"The sequence '##' is not allowed in a block name, " +
                f"it is reserved to internal mechanisms.\n"
            )
            raise ExtensionError(message, modname="sphinx_literate")

        key = lit.key
        existing = self._blocks.get(key)

        if existing is not None:
            maybe_root = ''
            if lit.tangle_root is not None:
                maybe_root = f" (in root '{lit.tangle_root}')"
            message = (
                f"Multiple literate code blocks with the same name '{lit.name}'{maybe_root} were found:\n" +
                f"  - In document '{existing.docname}', line {existing.lineno}.\n"
                f"  - In document '{lit.docname}', line {lit.lineno}.\n"
            )
            raise ExtensionError(message, modname="sphinx_literate")

        self._blocks[key] = lit

    def append_codeblock(self, lit: CodeBlock) -> None:
        """
        Append the content of the code block to the code block that already has
        the same name. Raises an exception if such a block does not exist.
        @param lit block to append
        """
        key = lit.key
        existing = self._blocks.get(key)

        if existing is None:
            maybe_root = ''
            if lit.tangle_root is not None:
                maybe_root = f" (in root '{lit.tangle_root}')"
            message = (
                f"Trying to append to a non existing literate code blocks '{lit.name}'{maybe_root}"
            )
            raise ExtensionError(message, modname="sphinx_literate")

        # Insert at the end of the child list
        while existing.next is not None:
            existing = existing.next
        existing.next = lit
        lit.prev = existing

        # Update child index for 'lit' and its children
        child_index = existing.child_index + 1
        while lit is not None:
            lit.child_index = child_index
            child_index += 1
            lit = lit.next

    def replace_codeblock(self, lit: CodeBlock) -> None:
        """
        Replace a block and all this children with a new one. Raises an
        exception if such a block does not exist.
        @param lit block to append
        """
        key = lit.key
        existing = self._blocks.get(key)

        if existing is None:
            maybe_root = ''
            if lit.tangle_root is not None:
                maybe_root = f" (in root '{lit.tangle_root}')"
            message = (
                f"Trying to replace a non existing literate code blocks '{lit.name}'{maybe_root}"
            )
            raise ExtensionError(message, modname="sphinx_literate")

        self._blocks[key] = lit

    def add_reference(self, referencer: Key, referencee: Key) -> None:
        """
        Signal that `referencer` contains a reference to `referencee`
        """
        self._references[referencee].add(referencer)

    def merge(self, other: CodeBlockRegistry) -> None:
        """
        Merge antoher registry into this one.
        """
        for lit in other.blocks():
            self.add_codeblock(lit, refs)
        for key, refs in other._references.items():
            self._references[key].update(refs)

    def remove_codeblocks_by_docname(self, docname: str) -> None:
        # TODO: when supporting cross-document REPLACE, be careful here
        self._blocks = {
            key: lit
            for key, lit in self._blocks.items()
            if lit.docname != docname
        }

    def set_tangle_parent(self, tangle_root: str, parent: str, docname: str, lineno: int) -> None:
        """
        Set the parent for a given tangle root. Fail if a different root has
        already been defined.
        @param tangle_root name of the tangle root for which we define a parent
        @param parent name of the tangle to set as parent
        @param docname Name of the document that sets this parenting
        @param lineno Line where the lit-config that sets this is defined
        """
        existing = self._hierarchy.get(tangle_root)
        if existing is not None:
            if existing.parent != parent:
                message = (
                    f"Attempting to set the tangle parent for root '{tangle_root}' to a different value:\n" +
                    f"  Was set to '{existing.parent}' in document '{existing.docname}', line {existing.lineno}.\n"
                    f"  But trying to set to '{parent}' in document '{docname}', line {lineno}.\n"
                )
                raise ExtensionError(message, modname="sphinx_literate")
        else:
            self._hierarchy[tangle_root] = TangleHierarchyEntry(
                root = tangle_root,
                parent = parent,
                docname = docname,
                lineno = lineno
            )

    def blocks(self) -> CodeBlock:
        return self._blocks.values()

    def get_by_key(self, key: Key) -> CodeBlock:
        return self._blocks.get(key)

    def get(self, name: str, tangle_root: str | None = None) -> CodeBlock:
        return self.get_by_key(CodeBlock.build_key(name, tangle_root))

    def keys(self, key: Key) -> dict_keys:
        return self._blocks.keys()

    def items(self) -> dict_items:
        return self._blocks.items()

    def references_to_key(self, key: Key) -> List[Key]:
        return list(self._references[key])
