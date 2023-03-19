"""
sphinx_literate is an extension inspired by the concept of Literate Programming

It provides a directive close to code blocks, called `lit`. The author can
specify how these literate code blocks should be assembled together in order to
produce the full code that is presented in the documentation.

Let's take a very simple example:

```{lit} Base skeleton
#include <iostream>
int main(int, char**) {
    {{Main content}}
}
```

And we can later define the main content:

```{lit} C++, Main content
std::cout << "Hello world" << std::endl;
```

This naming provides 2 complementzary features:

 1. The documentation's source code can be transformed into a fully working
    code. This is traditionnaly called the **tangled** code.

 2. The documentation can display links that help navigating through the code
    even though the documentation presents it non-linearily.

**NB** The syntax for referencing other code blocks is `<<Some block name>>`
by default, but as this may conflict with the syntax of your programming
language, you can customize it with the options `lit_begin_ref` and
`lit_end_ref`.

**NB** The language lexer name (C++ in the example above) is optional, and
provided as a first token separated from the block name by a comma (,).

When the block name starts with "file:", the block is considered as the root
and the remaining of the name is the path of the file into which the tangled
content must be saved, relative to the root tangle directory.

"""

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import Directive
from docutils.statemachine import StringList, State, StateMachine

import sphinx
from sphinx.locale import _
from sphinx.util.docutils import SphinxDirective
from sphinx.errors import ExtensionError
from sphinx.util.fileutil import copy_asset_file

from dataclasses import dataclass
from copy import deepcopy
import re
import random
import os

from .builder import TangleBuilder
from .registry import CodeBlock, CodeBlockRegistry
from .tangle import tangle
from .directives import setup as setup_directives
from .config import setup as setup_config
from .nodes import setup as setup_nodes
from .nodes import LiterateNode, TangleNode

from docutils import nodes

####################################################

def purge_lit_codeblocks(app, env, docname):
    lit_codeblocks = CodeBlockRegistry.from_env(env)
    lit_codeblocks.remove_codeblocks_by_docname(docname)

def merge_lit_codeblocks(app, env, docnames, other):
    lit_codeblocks = CodeBlockRegistry.from_env(env)
    lit_codeblocks.merge(CodeBlockRegistry.from_env(other))

def process_literate_nodes(app, doctree, fromdocname):
    lit_codeblocks = CodeBlockRegistry.from_env(app.builder.env)

    for literate_node in doctree.findall(LiterateNode):
        literate_node.uid_to_lit = {
            h: lit_codeblocks.get_rec_by_key(key)
            for h, key in literate_node.uid_to_block_key.items()
        }
        literate_node.references = [
            lit_codeblocks.get_by_key(k)
            for k in lit_codeblocks.references_to_key(literate_node.lit.key)
        ]

    for tangle_node in doctree.findall(TangleNode):

        tangled_content, lit = tangle(
            tangle_node.block_name,
            tangle_node.tangle_root,
            lit_codeblocks,
            app.config,
            f"in tangle directive from {tangle_node.source_location.format()}, "
        )

        para = nodes.paragraph()
        para += nodes.Text(f"Tangled block '{lit.name}' [from ")

        refnode = nodes.reference('', '')
        refnode['refdocname'] = lit.source_location.docname
        refnode['refuri'] = lit.link_url(fromdocname, app.builder)
        refnode.append(nodes.emphasis(_('here'), _('here')))
        para += refnode
        
        para += nodes.Text("]")

        lexer = tangle_node.lexer
        if lexer is None:
            lexer = lit.lexer

        block_node = tangle_node.raw_block_node
        block_node.args = [lexer] if lexer is not None else []
        block_node.rawsource = '\n'.join(tangled_content)
        if lexer is not None:
            block_node['language'] = lexer
        block_node.children.clear()
        block_node.children.append(nodes.Text(block_node.rawsource))

        tangle_node.replace_self([para, block_node])

def copy_custom_files(app, exc):
    if app.config.lit_use_default_style:
        asset_files = [
            "js/sphinx_literate.js",
        ]
    else:
        asset_files = []
    if app.builder.format == 'html' and not exc:
        staticdir = os.path.join(app.builder.outdir, '_static')
        root = os.path.dirname(__file__)
        for path in asset_files:
            copy_asset_file(os.path.join(root, path), staticdir)

#############################################################
# Setup

def setup(app):
    setup_config(app)

    setup_nodes(app)

    setup_directives(app)

    app.connect('doctree-resolved', process_literate_nodes)
    app.connect('env-purge-doc', purge_lit_codeblocks)
    app.connect('env-merge-info', merge_lit_codeblocks)
    app.connect('build-finished', copy_custom_files)

    app.add_builder(TangleBuilder)

    app.add_js_file("sphinx_literate.js")

    return {
        'version': '0.2',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
