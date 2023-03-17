from typing import List

from docutils import nodes
from docutils.nodes import Node, Element
from docutils.parsers.rst import directives
from docutils.statemachine import StringList

from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec
from sphinx.directives.code import CodeBlock as SphinxCodeBlock
from sphinx.application import Sphinx

from .parse import parse_block_content
from .registry import CodeBlock, CodeBlockRegistry
from .nodes import LiterateNode, TangleNode

#############################################################

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

#############################################################

class LiterateSetupDirective(SphinxDirective):
    """
    Directive to set local options for sphinx_literate.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec: OptionSpec = {
        'force': directives.flag,
        'linenothreshold': directives.positive_int,
        'tangle-root': directives.unchanged
    }

    def run(self) -> List[Node]:
        tangle_root = self.options.get('tangle-root')
        force = 'force' in self.options

        self.env.temp_data['tangle-root'] = tangle_root
        return []

#############################################################

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

#############################################################

class LiterateDirective(SphinxCodeBlock, DirectiveMixin):

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        self.parse_arguments()
        tangle_root = self.env.temp_data.get('tangle-root')
        self.parsed_content = parse_block_content(self.content, tangle_root, self.config)

        targetid = 'lit-%d' % self.env.new_serialno('lit')
        targetnode = nodes.target('', '', ids=[targetid])

        self.lit = CodeBlock(
            name=self.arg_name,
            docname=self.env.docname,
            lineno=self.lineno,
            content=self.content,
            target=targetnode,
            lexer=self.arg_lexer,
            tangle_root=tangle_root,
        )

        lit_codeblocks = CodeBlockRegistry.from_env(self.env)
        lit_codeblocks.add_codeblock(self.lit)

        # Call parent for generating a regular code block
        self.content = StringList(self.parsed_content.content)
        self.arguments = [self.arg_lexer] if self.arg_lexer is not None else []

        block_node = self.create_block_node()

        return [targetnode, block_node]

    def create_block_node(self):
        """
        Call parent class' run to create a code block, and post process it to
        inject our literate code block.
        """
        raw_block_node = super().run()[0]

        if isinstance(raw_block_node, nodes.literal_block):
            block_node = nodes.container(classes=['literal-block-wrapper'])
            block_node += self.wrap_literal_node(raw_block_node)
        else:
            new_children = []
            for node in raw_block_node:
                if isinstance(node, nodes.literal_block):
                    node = self.wrap_literal_node(node)
                new_children.append(node)
            block_node = raw_block_node
            block_node.children = new_children

        block_node['classes'].append("lit-block-wrapper")
        return block_node

    def wrap_literal_node(self, raw_literal_node):
        """
        Wrap Sphinx literal node with our literate node, which contains context
        about what reference links to insert during the final translation.
        """
        literate_node = LiterateNode(raw_literal_node, self.lit)
        literate_node.hashcode_to_block_key = self.parsed_content.uid_to_block_key
        return literate_node

#############################################################

def setup(app: Sphinx) -> None:
    app.add_directive("lit-setup", LiterateSetupDirective)
    app.add_directive("lit", LiterateDirective)
    app.add_directive("tangle", TangleDirective)
