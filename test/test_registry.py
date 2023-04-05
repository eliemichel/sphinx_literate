import sys
from os.path import join, dirname
sys.path.append(join(dirname(dirname(__file__)), "_extensions"))

from sphinx_literate.registry import CodeBlockRegistry, CodeBlock

from sphinx.errors import ExtensionError
from unittest import TestCase, main

class TestRegistryBasics(TestCase):
    def test_multiple_tangle_parents(self):
        reg = CodeBlockRegistry()
        # Can have multiple children for the same parent tangle "A"
        reg.set_tangle_parent("B", "A")
        reg.set_tangle_parent("C", "A")

        # Cannot have multiple parents for the same tangle "B""
        def dont():
            reg.set_tangle_parent("B", "D")
        self.assertRaises(ExtensionError, dont)

class TestRegistryMerge(TestCase):
    def test_merge_simple(self):
        reg_a = CodeBlockRegistry()
        reg_a.register_codeblock(CodeBlock(
            name = "Block A1",
            content = ["A1"],
        ))
        reg_a.register_codeblock(CodeBlock(
            name = "Block A2",
            content = ["A2"],
        ))

        reg_b = CodeBlockRegistry()
        reg_b.register_codeblock(CodeBlock(
            name = "Block B1",
            content = ["B1"],
        ))
        reg_b.register_codeblock(CodeBlock(
            name = "Block A1",
            content = ["B2"],
        ), ['REPLACE'])

        self.assertEqual(reg_a._missing, [])
        self.assertEqual(len(reg_b._missing), 1)
        self.assertEqual(reg_b._missing[0].key, CodeBlock.build_key("Block A1"))

        reg_a.merge(reg_b)

        self.assertEqual(reg_a._missing, [])
        self.assertEqual(list(reg_a.get("Block A1").all_content()), ["B2"])

        reg_a.check_integrity()

    def test_merge_missing(self):
        reg_a = CodeBlockRegistry()
        reg_a.register_codeblock(CodeBlock(
            name = "Block A1",
            content = ["A1"],
        ))
        reg_a.register_codeblock(CodeBlock(
            name = "Block A2",
            content = ["A2"],
        ))

        reg_b = CodeBlockRegistry()
        reg_b.register_codeblock(CodeBlock(
            name = "Block B1",
            content = ["B1"],
        ))
        reg_b.register_codeblock(CodeBlock(
            name = "Block C1",
            content = ["B2"],
        ), ['REPLACE'])

        self.assertEqual(reg_a._missing, [])
        self.assertEqual(len(reg_b._missing), 1)
        self.assertEqual(reg_b._missing[0].key, CodeBlock.build_key("Block C1"))

        reg_a.merge(reg_b)

        self.assertEqual(len(reg_a._missing), 1)
        self.assertEqual(reg_a._missing[0].key, CodeBlock.build_key("Block C1"))

        self.assertRaises(ExtensionError, reg_a.check_integrity)

    def test_merge_multi_root(self):
        reg_a = CodeBlockRegistry()
        reg_a.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "A",
            content = ["A1"],
        ))
        reg_a.register_codeblock(CodeBlock(
            name = "Block A2",
            tangle_root = "A",
            content = ["A2"],
        ))

        reg_b = CodeBlockRegistry()
        reg_b.register_codeblock(CodeBlock(
            name = "Block B1",
            tangle_root = "B",
            content = ["B1"],
        ))
        reg_b.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "B",
            content = ["B2"],
        ), ['REPLACE'])

        self.assertEqual(reg_a._missing, [])
        self.assertEqual(len(reg_b._missing), 1)
        self.assertEqual(reg_b._missing[0].key, CodeBlock.build_key("Block A1", "B"))

        reg_a.merge(reg_b)

        # No relation between A and B -> key still missing
        self.assertEqual(len(reg_a._missing), 1)
        self.assertEqual(reg_a._missing[0].key, CodeBlock.build_key("Block A1", "B"))

        self.assertRaises(ExtensionError, reg_a.check_integrity)

    def test_merge_parented_root(self):
        reg_a = CodeBlockRegistry()
        reg_a.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "A",
            content = ["A1"],
        ))
        reg_a.register_codeblock(CodeBlock(
            name = "Block A2",
            tangle_root = "A",
            content = ["A2"],
        ))

        reg_b = CodeBlockRegistry()
        reg_b.set_tangle_parent("B", "A")
        reg_b.register_codeblock(CodeBlock(
            name = "Block B1",
            tangle_root = "B",
            content = ["B1"],
        ))
        reg_b.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "B",
            content = ["B2"],
        ), ['REPLACE'])

        self.assertEqual(reg_a._missing, [])
        self.assertEqual(len(reg_b._missing), 1)
        self.assertEqual(reg_b._missing[0].key, CodeBlock.build_key("Block A1", "B"))

        reg_a.merge(reg_b)

        # B is child of A -> merged 'replace' op
        self.assertEqual(reg_a._missing, [])
        self.assertEqual(list(reg_a.get("Block A1", "A").all_content()), ["A1"])
        self.assertEqual(list(reg_a.get("Block A1", "B").all_content()), ["B2"])

        reg_a.check_integrity()

    def test_merge_late_parented_root(self):
        reg_a = CodeBlockRegistry()
        reg_a.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "A",
            content = ["A1"],
        ))
        reg_a.register_codeblock(CodeBlock(
            name = "Block A2",
            tangle_root = "A",
            content = ["A2"],
        ))

        reg_b = CodeBlockRegistry()
        reg_b.register_codeblock(CodeBlock(
            name = "Block B1",
            tangle_root = "B",
            content = ["B1"],
        ))
        reg_b.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "B",
            content = ["B2"],
        ), ['REPLACE'])

        self.assertEqual(reg_a._missing, [])
        self.assertEqual(len(reg_b._missing), 1)
        self.assertEqual(reg_b._missing[0].key, CodeBlock.build_key("Block A1", "B"))

        reg_a.merge(reg_b)

        # Set parent after merge, this should still work
        reg_a.set_tangle_parent("B", "A")

        # B is child of A -> merged 'replace' op
        self.assertEqual(reg_a._missing, [])
        self.assertEqual(list(reg_a.get("Block A1", "A").all_content()), ["A1"])
        self.assertEqual(list(reg_a.get("Block A1", "B").all_content()), ["B2"])

        reg_a.check_integrity()

    def test_merge_hierarchies(self):
        reg_a = CodeBlockRegistry()
        reg_a.set_tangle_parent("A", "X")
        
        reg_b = CodeBlockRegistry()
        reg_b.set_tangle_parent("B", "Y")

        reg_a.merge(reg_b)

        self.assertEqual(reg_a._parent_tangle_root("A"), "X")
        self.assertEqual(reg_a._parent_tangle_root("B"), "Y")

    def test_cannot_define_contradictory_parents(self):
        reg_a = CodeBlockRegistry()
        reg_a.set_tangle_parent("A", "X")

        reg_b = CodeBlockRegistry()
        reg_b.set_tangle_parent("A", "Y")

        def dont():
            reg_a.merge(reg_b)
        self.assertRaises(ExtensionError, dont)

    def test_insert(self):
        reg = CodeBlockRegistry()
        reg.register_codeblock(CodeBlock(
            name = "Block A1",
            content = ["Hello, world", "Lorem ipsum"],
        ))
        reg.register_codeblock(CodeBlock(
            name = "Block A2",
            content = ["Inserted"],
        ), [('INSERT', 'Block A1', 'AFTER', "Hello")])
        reg.register_codeblock(CodeBlock(
            name = "Block A2",
            content = ["lines"],
        ), ['APPEND'])

        self.assertEqual(list(reg.get("Block A1").all_content()), [
            "Hello, world",
            "Inserted",
            "lines",
            "Lorem ipsum",
        ])

    def test_insert_with_parent(self):
        reg = CodeBlockRegistry()
        reg.set_tangle_parent("B", "A")
        reg.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "A",
            content = ["Hello, world", "Lorem ipsum"],
        ))
        reg.register_codeblock(CodeBlock(
            name = "Block A2",
            tangle_root = "B",
            content = ["Inserted"],
        ), [('INSERT', 'Block A1', 'AFTER', "Hello")])
        reg.register_codeblock(CodeBlock(
            name = "Block A2",
            tangle_root = "B",
            content = ["lines"],
        ), ['APPEND'])

        block_A1_A = reg.get("Block A1", "A")
        block_A1_B = reg.get("Block A1", "B")
        block_A2_B = reg.get("Block A2", "B")
        self.assertNotEqual(block_A1_B, None)
        self.assertEqual(block_A1_B.relation_to_prev, 'INSERT')
        self.assertEqual(block_A2_B.relation_to_prev, 'INSERTED')
        self.assertEqual(block_A1_B.prev, block_A1_A)

        self.assertEqual(list(reg.get("Block A1", "A").all_content()), [
            "Hello, world",
            "Lorem ipsum",
        ])

        self.assertEqual(list(reg.get("Block A1", "B").all_content()), [
            "Hello, world",
            "Inserted",
            "lines",
            "Lorem ipsum",
        ])

    def test_insert_with_merged_parent(self):
        reg_a = CodeBlockRegistry()
        reg_a.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "A",
            content = ["Hello, world", "Lorem ipsum"],
        ))
        reg_b = CodeBlockRegistry()
        reg_b.set_tangle_parent("B", "A")
        reg_b.register_codeblock(CodeBlock(
            name = "Block A2",
            tangle_root = "B",
            content = ["Inserted"],
        ), [('INSERT', 'Block A1', 'AFTER', "Hello")])
        reg_b.register_codeblock(CodeBlock(
            name = "Block A2",
            tangle_root = "B",
            content = ["lines"],
        ), ['APPEND'])

        reg = reg_a
        reg.merge(reg_b)

        reg.check_integrity()

        block_A1_A = reg.get("Block A1", "A")
        block_A1_B = reg.get("Block A1", "B")
        block_A2_B = reg.get("Block A2", "B")
        self.assertNotEqual(block_A1_B, None)
        self.assertEqual(block_A1_B.relation_to_prev, 'INSERT')
        self.assertEqual(block_A2_B.relation_to_prev, 'INSERTED')
        self.assertEqual(block_A1_B.prev, block_A1_A)

        self.assertEqual(list(reg.get("Block A1", "A").all_content()), [
            "Hello, world",
            "Lorem ipsum",
        ])

        self.assertEqual(list(reg.get("Block A1", "B").all_content()), [
            "Hello, world",
            "Inserted",
            "lines",
            "Lorem ipsum",
        ])

    def test_non_linear_parenting(self):
        reg = CodeBlockRegistry()
        reg.set_tangle_parent("B", "A")

        # First append in child
        reg.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "B",
            content = ["Line 2"],
        ), ['APPEND'])

        self.assertEqual(len(reg._missing), 1)
        self.assertEqual(reg._missing[0].key, CodeBlock.build_key("Block A1", "B"))

        # Then define in parent
        reg.register_codeblock(CodeBlock(
            name = "Block A1",
            tangle_root = "A",
            content = ["Line 1"],
        ))

        reg.check_integrity()

        self.assertEqual(list(reg.get("Block A1", "A").all_content()), [
            "Line 1",
        ])
        self.assertEqual(list(reg.get("Block A1", "B").all_content()), [
            "Line 1",
            "Line 2",
        ])

    def test_non_linear_parenting_with_insert(self):
        reg = CodeBlockRegistry()
        reg.set_tangle_parent("B", "A")

        # First insert in child
        block_b1 = CodeBlock(
            name = "Block B1",
            tangle_root = "B",
            content = ["Foo"],
        )
        reg.register_codeblock(block_b1, [('INSERT', 'Block A1', 'AFTER', "Line 1")])

        self.assertEqual(len(reg._missing), 1)
        self.assertEqual(reg._missing[0].key, CodeBlock.build_key("Block A1", "B"))

        modifier = reg.get("Block B1", "B").prev
        self.assertNotEqual(modifier, None)
        self.assertEqual(modifier.inserted_block, reg.get("Block B1", "B"))
        self.assertEqual(modifier.prev, None)
        old_modifier = modifier

        # Then define in parent
        block_a1 = CodeBlock(
            name = "Block A1",
            tangle_root = "A",
            content = ["Line 1", "Line 2"],
        )
        reg.register_codeblock(block_a1)

        reg.check_integrity()

        self.assertEqual(list(reg.get("Block A1", "A").all_content()), [
            "Line 1",
            "Line 2",
        ])
        self.assertEqual(list(reg.get("Block A1", "B").all_content()), [
            "Line 1",
            "Foo",
            "Line 2",
        ])
        modifier = reg.get("Block B1", "B").prev
        self.assertNotEqual(modifier, None)
        self.assertEqual(modifier.inserted_block, reg.get("Block B1", "B"))
        self.assertEqual(modifier.prev, reg.get("Block A1", "A"))

        self.assertEqual(block_b1, reg.get("Block B1", "B"))
        self.assertEqual(block_a1, reg.get("Block A1", "A"))
        self.assertEqual(modifier, reg.get("Block A1", "B"))
        self.assertEqual(modifier, old_modifier)

    def test_non_linear_parenting_with_merge(self):
        reg_a = CodeBlockRegistry()
        reg_b = CodeBlockRegistry()
        reg_b.set_tangle_parent("B", "A")

        # First insert in child
        block_b1 = CodeBlock(
            name = "Block B1",
            tangle_root = "B",
            content = ["Foo"],
        )
        reg_b.register_codeblock(block_b1, [('INSERT', 'Block A1', 'AFTER', "Line 1")])

        self.assertEqual(len(reg_b._missing), 1)
        self.assertEqual(reg_b._missing[0].key, CodeBlock.build_key("Block A1", "B"))

        modifier = reg_b.get("Block B1", "B").prev
        self.assertNotEqual(modifier, None)
        self.assertEqual(modifier.inserted_block, reg_b.get("Block B1", "B"))
        self.assertEqual(modifier.prev, None)
        old_modifier = modifier

        # Then define in parent
        block_a1 = CodeBlock(
            name = "Block A1",
            tangle_root = "A",
            content = ["Line 1", "Line 2"],
        )
        reg_a.register_codeblock(block_a1)

        reg = reg_b
        reg.merge(reg_a)

        reg.check_integrity()

        self.assertEqual(list(reg.get("Block A1", "A").all_content()), [
            "Line 1",
            "Line 2",
        ])
        self.assertEqual(list(reg.get("Block A1", "B").all_content()), [
            "Line 1",
            "Foo",
            "Line 2",
        ])
        modifier = reg.get("Block B1", "B").prev
        self.assertNotEqual(modifier, None)
        self.assertEqual(modifier.inserted_block, reg.get("Block B1", "B"))
        self.assertEqual(modifier.prev, reg.get("Block A1", "A"))

        self.assertEqual(block_b1, reg.get("Block B1", "B"))
        self.assertEqual(block_a1, reg.get("Block A1", "A"))
        self.assertEqual(modifier, reg.get("Block A1", "B"))
        self.assertEqual(modifier, old_modifier)
        

if __name__ == "__main__":
    main()
