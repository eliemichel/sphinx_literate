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
from sphinx.directives.code import CodeBlock as SphinxCodeBlock

from dataclasses import dataclass
from copy import deepcopy
import re
import random
import html
import os

from .builder import TangleBuilder
from .registry import CodeBlock, CodeBlockRegistry
from .tangle import tangle
from .directives import setup as setup_directives
from .config import setup as setup_config

#############################################################
# Elements

class TangleNode(nodes.General, nodes.Element):
    def __init__(self, root_block_name, lexer, docname, lineno, raw_block_node, tangle_root, *args):
        self.lexer = lexer
        self.root_block_name = root_block_name
        self.docname = docname
        self.lineno = lineno
        self.raw_block_node = raw_block_node
        self.tangle_root = tangle_root

        super().__init__(*args)

class LiterateHighlighter:
    """
    A custom code block highlighter that uses an existing highlighter and
    insert custom links for references to other code blocks
    """
    def __init__(self, original_highlighter, node, ref_factory):
        self._original_highlighter = original_highlighter
        self.node = node
        self.ref_factory = ref_factory

    def highlight_block(self, rawsource, lang, **kwargs):
        # Pre-process is done by the LiterateDirective

        highlighted = self._original_highlighter.highlight_block(rawsource, lang, **kwargs)

        # Post-process: Replace hashes with links
        for hashcode, lit in self.node.hashcode_to_lit.items():
            ref = self.ref_factory(self.node, lit)
            highlighted = highlighted.replace(hashcode, ref)

        return highlighted

class LiterateNode(nodes.General, nodes.Element):
    def __init__(self, literal_node, lit, *args):
        """
        We wrap a literal node and insert links to references code blocks
        """
        self._literal_node = literal_node
        self.hashcode_to_block_key = {}
        self.hashcode_to_lit = {}
        self.lit = lit
        super().__init__(*args)

    @classmethod
    def build_translation_handlers(cls, app):
        """
        This is a hack for inheriting the literal_block visitors so that we
        support as many builders as possible.
        (Feel free to suggest a better way...)
        """
        literal_block_handlers = {}
        reference_handlers = {}
        for name, builder in app.registry.builders.items():
            default = builder.default_translator_class
            translator_class = app.registry.translators.get(
                name,
                default.fget(app) if type(default) == property else default
            )
            if translator_class is None:
                continue
            literal_block_handlers[name] = (
                translator_class.visit_literal_block,
                translator_class.depart_literal_block
            )
            reference_handlers[name] = (
                translator_class.visit_reference,
                translator_class.depart_reference
            )

        inherited_html_visit, inherited_html_depart = literal_block_handlers.get('html', (None, None))

        def create_ref(node, lit):
            """
            # TODO: Could this be a way to make that protable to all builders?
            refnode = nodes.reference('', '')
            refnode['refdocname'] = lit.docname
            refnode['refuri'] = (
                app.builder.get_relative_uri(node.document['source'], lit.docname)
                + '#' + lit.target['refid']
            )
            refnode.append(nodes.Text(lit.name))
            """
            lit_id = lit.target['refid']
            return (
                app.config.lit_begin_ref +
                f'<a href="#{lit_id}">{lit.name}</a>' +
                app.config.lit_end_ref
            )

        def visit_html(self, node):
            # Override highlighter
            original_highlighter = self.highlighter
            self.highlighter = LiterateHighlighter(original_highlighter, node, create_ref)

            # Copy anchoring properties from wrapper node to internal node
            node._literal_node['ids'] = node['ids']
            node._literal_node['names'] = node['names']
            for prop in ['expect_referenced_by_name', 'expect_referenced_by_id']:
                if hasattr(node, prop):
                    setattr(node._literal_node, prop, getattr(node, prop))

            # Call inherited visitor
            try:
                inherited_html_visit(self, node._literal_node)
                skip = False
            except nodes.SkipNode:
                skip = True
            
            # Restore highlighter
            self.highlighter = original_highlighter

            # Footer
            self.body.append(
                '<div class="lit-block-footer">' +
                html.escape(app.config.lit_begin_ref) +
                ' <span class="lit-name">' +
                html.escape(node.lit.name) +
                '</span> ' +
                html.escape(app.config.lit_end_ref) +
                '</div>'
            )

            if skip:
                raise nodes.SkipNode

        def depart_html(self, node):
            inherited_html_depart(self, node._literal_node)

        literal_block_handlers['html'] = (
            visit_html,
            depart_html,
        )
        return literal_block_handlers

#############################################################
# Directives

class DirectiveMixin:
    def parse_arguments(self):
        self.arg_lexer = None
        self.arg_name = ""

        raw_args = self.arguments[0]
        tokens = raw_args.split(",")
        if len(tokens) == 1:
            self.arg_name = tokens[0]
        elif len(tokens) == 2:
            self.arg_lexer = tokens[0].strip()
            self.arg_name = tokens[1].strip()
        else:
            message = (
                f"Invalid block name: '{raw_args}'\n" +
                "At most 1 comma is allowed, to specify the language, but the name cannot contain a comma."
            )
            raise ExtensionError(message, modname="sphinx_literate")

class TangleDirective(SphinxCodeBlock, DirectiveMixin):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        self.parse_arguments()

        self.content = StringList(["Hello, world"])
        self.arguments = [self.arg_lexer] if self.arg_lexer is not None else []

        raw_block_node = super().run()[0]
        tangle_root = self.env.temp_data.get('tangle-root')

        return [
            TangleNode(
                self.arg_name,
                self.arg_lexer,
                self.env.docname,
                self.lineno,
                raw_block_node,
                tangle_root
            )
        ]

class LiterateDirective(SphinxCodeBlock, DirectiveMixin):

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        self.parse_arguments()
        self.parse_content()
        self.tangle_root = self.env.temp_data.get('tangle-root')

        targetid = 'lit-%d' % self.env.new_serialno('lit')
        targetnode = nodes.target('', '', ids=[targetid])

        self.register_lit(targetnode)

        # Call parent for generating a regular code block
        self.content = StringList(self.parsed_source.split('\n'))
        self.arguments = [self.arg_lexer] if self.arg_lexer is not None else []

        raw_block_node = super().run()[0]

        def postprocess_literal_node(raw_literal_node):
            literate_node = LiterateNode(raw_literal_node, self.lit)
            literate_node.hashcode_to_blockname = {
                CodeBlock.build_key(name, self.tangle_root)
                for k, name in self.hashcode_to_blockname.items()
            }
            return literate_node

        if isinstance(raw_block_node, nodes.literal_block):
            block_node = nodes.container(classes=['literal-block-wrapper'])
            block_node += postprocess_literal_node(raw_block_node)
        else:
            new_children = []
            for node in raw_block_node:
                if isinstance(node, nodes.literal_block):
                    node = postprocess_literal_node(node)
                new_children.append(node)
            block_node = raw_block_node
            block_node.children = new_children

        block_node['classes'].append("lit-block-wrapper")

        return [targetnode, block_node]

    def register_lit(self, targetnode):
        self.lit = CodeBlock(
            name=self.arg_name,
            docname=self.env.docname,
            lineno=self.lineno,
            content=self.content,
            target=targetnode,
            lexer=self.arg_lexer,
            tangle_root=self.tangle_root,
        )

        lit_codeblocks = CodeBlockRegistry.from_env(self.env)
        lit_codeblocks.add_codeblock(self.lit)

    def parse_content(self):
        """
        This reads the raw source code and extracts {{references}} to other blocks.
        Populate self.parsed_source and self.hashcode_to_blockname
        """
        rawsource = '\n'.join(self.content)

        # Pre-process: We replace all code refs with a random hash, not to
        # disturb the syntax highlighter.
        offset = 0
        self.parsed_source = ""
        self.hashcode_to_blockname = {}
        begin_ref = self.config.lit_begin_ref
        end_ref = self.config.lit_end_ref
        while True:
            begin_offset = rawsource.find(begin_ref, offset)
            if begin_offset == -1:
                break
            end_offset = rawsource.find(end_ref, begin_offset)
            if end_offset == -1:
                break
            hashcode = "_" + "".join([random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(32)])
            blockname = rawsource[begin_offset+len(begin_ref):end_offset]
            self.hashcode_to_blockname[hashcode] = blockname
            self.parsed_source += rawsource[offset:begin_offset]
            self.parsed_source += hashcode
            offset = end_offset + len(end_ref)
        self.parsed_source += rawsource[offset:]

def purge_lit_codeblocks(app, env, docname):
    lit_codeblocks = CodeBlockRegistry.from_env(env)
    lit_codeblocks.remove_codeblocks_by_docname(docname)

def merge_lit_codeblocks(app, env, docnames, other):
    lit_codeblocks = CodeBlockRegistry.from_env(env)

    for lit in CodeBlockRegistry.from_env(other).blocks():
        lit_codeblocks.add_codeblock(lit)

def process_literate_nodes(app, doctree, fromdocname):
    lit_codeblocks = CodeBlockRegistry.from_env(app.builder.env)

    for literate_node in doctree.findall(LiterateNode):
        literate_node.hashcode_to_lit = {
            h: lit_codeblocks.get_by_key(key)
            for h, key in literate_node.hashcode_to_block_key.items()
        }

    for tangle_node in doctree.findall(TangleNode):
        lit = lit_codeblocks.get(tangle_node.root_block_name)
        if lit is None:
            message = (
                f"Literate code block not found: '{tangle_node.root_block_name}' " +
                f"(in tangle directive from document {tangle_node.docname}, line {tangle_node.lineno})"
            )
            raise ExtensionError(message, modname="sphinx_literate")

        para = nodes.paragraph()
        para += nodes.Text(f"Tangled block '{lit.name}' [from ")

        refnode = nodes.reference('', '')
        refnode['refdocname'] = lit.docname
        refnode['refuri'] = (
            app.builder.get_relative_uri(fromdocname, lit.docname)
            + '#' + lit.target['refid']
        )
        refnode.append(nodes.emphasis(_('here'), _('here')))
        para += refnode
        
        para += nodes.Text("]")

        tangled_content = tangle(
            tangle_node.root_block_name,
            tangle_node.tangle_root,
            lit_codeblocks,
            app.config,
        )

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

#############################################################
# Setup

def setup(app):
    app.add_config_value("lit_begin_ref", "{{", 'html', [str])
    app.add_config_value("lit_end_ref", "}}", 'html', [str])
    setup_config(app)

    app.add_node(TangleNode)
    app.add_node(LiterateNode, **LiterateNode.build_translation_handlers(app))

    app.add_directive("tangle", TangleDirective)
    app.add_directive("lit", LiterateDirective)
    setup_directives(app)

    app.connect('doctree-resolved', process_literate_nodes)
    app.connect('env-purge-doc', purge_lit_codeblocks)
    app.connect('env-merge-info', merge_lit_codeblocks)

    app.add_builder(TangleBuilder)

    return {
        'version': '0.2',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
