import sys
from os.path import join, dirname
sys.path.append(join(dirname(dirname(__file__)), "_extensions"))

from sphinx_literate.registry import CodeBlockRegistry, CodeBlock

from sphinx.errors import ExtensionError
from unittest import TestCase, main

class TestTangle(TestCase):
    def test_inherited_files(self):
        reg = CodeBlockRegistry()
        reg.set_tangle_parent("B", "A")
        block1 = CodeBlock(
            name = "file:foo.txt",
            tangle_root = "A",
            content = ["Lorem ipsum"],
        )
        reg.register_codeblock(block1)

        block2 = CodeBlock(
            name = "file:bar.txt",
            content = ["Dolor sit amet"],
        )
        reg.register_codeblock(block2)

        self.assertEqual(reg.get_rec("file:bar.txt", "A"), None)
        print([x.format() for x in reg.blocks_by_root("A")])

        self.assertEqual(len(reg.blocks_by_root("A")), 1)
        self.assertEqual(reg.blocks_by_root("A"), [block1])
        self.assertEqual(reg.blocks_by_root("B"), [block1])
        self.assertEqual(reg.blocks_by_root(None), [block2])

        self.assertTrue("A" in reg.all_tangle_roots())
        self.assertTrue("B" in reg.all_tangle_roots())
        self.assertTrue(None in reg.all_tangle_roots())

if __name__ == "__main__":
    main()
