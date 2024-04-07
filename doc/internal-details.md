Internal details
================

*These are some notes to myself about the way things are organized.*

## Introduction

Since D. Knuth introduced the idea of Literate Programming in the 80s `[Knuth84]`, numerous implementation targeting various programming languages have been proposed. None of them was satisfying enough to integrate in the context of an incremental programming course, so we present here our own. Our work is based on the Sphinx static site generator.

**NB:** The source of a tangling/weaving process is sometimes referred to as "hyper code" to highlight the fact that it has a different form than traditional source code.

*sphinx_literate* is a domain specific literate programming tool. Unlike for programming language, the "domain" to which this tool is specific is not the domain in which the end program runs, but rather the domain in which it is written. In our case, we target programs that are written for educational purpose, where the goal is to introduce step by step to a human reader the various bits of a programming library, framework or language (be it domain specific or general purpose). Our literate programming tool is not tailored for the redaction of a single long program, but rather a tree of incremental updates. Nonetheless, nothing prevents it from being used for the former case.

## Previous work

Some implementations target a specific programming language (HyperPerl `[Cunningham98]`, *Sweave* `[Leisch02]` and *knitr* `[Xie17]` for R), some do not. There is in general poor tooling support (syntax highlight for text editors, cross-platform support, etc.) either due to or causing a lack of adoption.

Existing implementations typically focus on a single document, which contrast with the way natural language text is now written. Initially tailored for monographic text releases, the conceptual tools provided by Literate Programming fail at playing along multi-page documentation and incremental courses that intend to tangle not only a whole program, but also it's history of steps, which are particularly interesting for learning purpose.

Notebook-based documents like what Jupyter provides are a particular case of literate programming. They offer more than weaving and tangling, in the sense that a document may be exported either as pure code, pure static document (e.g., HTML or PDF) but also as an interactive document.

Literate programming tool naturally tried to integrate into typesetting tools, such as (La)TeX (e.g., *Sweave* `[Leisch02]`). Ours integrates in Sphinx, a well established tool for static generation of library documentation websites. Some other tools reject the idea of getting tied with a documentation engine in favor of more general purpose transport format, such as XML `[Walsh02]`

*Knitr* `[Xie17]` tried to modularize.

## Background: Traditional literate programming

**Notebook.** The simplest case of literate programming is the one of notebooks (e.g., IPython/Jupyter). These are a sequence of interleaved text and code blocks meant to be both read and executed sequentially. Once executed, code blocks are followed by the output they generated, which gets stored in the document. The reader may choose to execute the document block by block, all at once, or not at all. Although it is possible to execute code blocks in an arbitrary order, it is a very error prone usage that is hard to expect from a third party reader when distributing the notebook as an end document.

Notebook are the most successful example of literate programming, and their Web-based interface enabled the development of various extension from the community. It is easy to customize the look and feel of a block's output, enabling the integration of input widgets such as sliders or even interactive 2D plot and 3D viewers. Their sequential layout is however a true limitation when it comes to writing long documents. Furthermore, their block-wise execution is a better fit for interpreted language than compiled ones.

**WEB.** WEB is Knuth's original implementation of their concept of Literate Programming, and led to many variations. This work introduces the vocable of *tangle* and *weave* to designate the generation of respectively the source code and the documentation from the original "hyper code" written by a human author. A key feature of WEB is the possibility to freely organize code *fragments* that are referencing each others to eventually build the entire target source code. This produces a "web" of fragments, hence the name (it is in effect a Directed Acyclic Graph). In some cases, tangling is a form of pre-processor that has no awareness of the underlying programming language. In more advanced setups, tangling may be specific to a programming language's syntax and thus able to e.g. rename identifiers.

**NB** These tools were born at a time where programming languages provided much less modularization tools and pretty much expected the programmer to write everything in single linear file, with a required ordering of definition that usually did not match the reasoning of the human writer. Besides maybe the C/C++ family that still rely on pre-processing hacks, all modern programming language now come with a proper definition of modules enabling the programmer and programming teams to split up code across multiple files and folders.

**NB** Contrary to WEB, we intend the tangled source code to be human-readable as well, and even be the base for third party reuse. WEB processors on the other hand may perform "uglyfication" to discourage the user from directly authoring it.

 - WEB
 - NoWeb http://www.cs.tufts.edu/~nr/noweb/
 - This approach assumes that the human-readable documentation, and thus the source code, is a single linear document. This is one of the key assumptions that we do not make in our work.

**Other.**

 - Leo https://web.archive.org/web/20130318150606/http://webpages.charter.net/edreamleo/front.html

**Examples.** Literate programming has been used for actual books, presenting for instance an ANSI C compiler `[Fraser91]`, a physically-based render engine `[Pharr23]`.

## Some elements of our approach

We support the following features:

 - Tangling generates a whole source tree rather than a single file.

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

## References

```
[Pharr23] Pharr, Matt, Wenzel Jakob, and Greg Humphreys. Physically based rendering: From theory to implementation. MIT Press, 2023.
[Xie17] Xie, Yihui. Dynamic Documents with R and knitr. Chapman and Hall/CRC, 2017.
[Leisch02] Leisch, Friedrich (2002). "[Sweave, Part I: Mixing R and LaTeX: A short introduction to the Sweave file format and corresponding R functions](https://cran.r-project.org/doc/Rnews/Rnews_2002-3.pdf)" (PDF). R News. 2 (3): 28–31. Retrieved 22 January 2012.
[Walsh02] "[Literate Programming in XML](https://nwalsh.com/docs/articles/xml2002/lp/paper.html)" (consulted on 2024-04-07)
[Fraser91] Fraser, Christopher W. "A retargetable compiler for ANSI C." ACM Sigplan Notices 26.10 (1991): 29-43.
[Cunningham98]: HyperPerl. http://code.fed.wiki.org/view/hyperperl (consulted on 2024-04-07)
[Knuth84]: Knuth, Donald Ervin. "Literate programming." The computer journal 27.2 (1984): 97-111.
```

Other sources and meta-sources:

 - https://wiki.c2.com/?LiterateProgramming
 - https://mirror.gutenberg-asso.fr/tex.loria.fr/english/litte.html
 - https://literateprograms.org/
 - http://xml.coverpages.org/xmlLitProg.html

Misc keywords:

 - program fragments
 - programming in the large
