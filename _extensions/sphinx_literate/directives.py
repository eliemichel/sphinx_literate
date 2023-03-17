from typing import List

from docutils.nodes import Node, Element
from docutils.parsers.rst import directives

from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec
from sphinx.application import Sphinx

class LiterateSetupNode(Element):
    """Inserted to set the highlight language and line number options for
    subsequent code blocks.
    """

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
        return [] #return [LiterateSetupNode(tangle_root=tangle_root)]

def setup(app: Sphinx) -> None:
    app.add_node(LiterateSetupNode)

    app.add_directive("lit-setup", LiterateSetupDirective)
