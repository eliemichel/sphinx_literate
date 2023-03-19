Internal details
================

*These are some notes to myself about the way things are organized.*

The overall tangle data that is extracted from the documentation's source is:

 - A tree of **tangle roots**, which may have a parent (so a forest more than a tree actually). A tangle root corresponds to a standalone source tree, and the same documentation can generate multiple source trees.

```Python
TangleRoot:
	id: TangleRootId (str)
	parent: TangleRootId | None
	blocks: LitBlockName -> Ref<LitBlock>
```

A tangle root is referenced by its name (a string), `TangleRootId` here.

 - A directed graph of **literate code blocks** (or just "lit blocks") that are defined throughout the documents. Each block is associated to one and only one tangle root. Blocks that have the same name and tangle root are sorted as a doubly linked list. They are ordered like defined in the documentation's source. Each block tells whether it must be appended to the previous one or replacing it. Implicitly, if the parent tangle root (or recursively one of its parents) contains a block with the same name, it is its "prev".

```Python
LitBlock:
	name: LitBlockName (str)
	tangle_root: TangleRootId

	# Linked list of appended blocks for the same name and tangle root
	next: Ref<LitBlock>
	prev: Ref<LitBlock>

```

A lit block is referenced by a tangle root, a name and a child index (position in the linked list), but usually the child index is not used.

The tangle root points to the first element of the list.
