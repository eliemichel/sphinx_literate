import sys
from os.path import join, dirname
sys.path.append(join(dirname(dirname(__file__)), "_extensions"))

from sphinx_literate.parse import parse_block_title

from sphinx.errors import ExtensionError
from unittest import TestCase, main

# Here are some tests, although the coverage is very low...

class TestBlockTitle(TestCase):
	def test_parser(self):
		"""
        Test that block titles are parsed correctly
        """
		raw_title = "Language, The title (some options)"
		parsed_title = parse_block_title(raw_title)
		self.assertEqual(parsed_title.lexer, "Language")
		self.assertEqual(parsed_title.name, "The title")
		self.assertEqual(parsed_title.options, {'SOME OPTIONS'})

		raw_title = "Another title (multiple, options) "
		parsed_title = parse_block_title(raw_title)
		self.assertIsNone(parsed_title.lexer)
		self.assertEqual(parsed_title.name, "Another title")
		self.assertEqual(parsed_title.options, {'OPTIONS', 'MULTIPLE'})

		raw_title = "C++, Hello world"
		parsed_title = parse_block_title(raw_title)
		self.assertEqual(parsed_title.lexer, "C++")
		self.assertEqual(parsed_title.name, "Hello world")
		self.assertEqual(parsed_title.options, set())

		raw_title = "C++, Hello world (again)"
		parsed_title = parse_block_title(raw_title)
		self.assertEqual(parsed_title.lexer, "C++")
		self.assertEqual(parsed_title.name, "Hello world")
		self.assertEqual(parsed_title.options, {'AGAIN'})

	def test_parser_advanced(self):
		raw_title = r'C++, Change stuff (insert in {{bla}} after "hey, there is a comma and a parenthese ), how nice?")'
		parsed_title = parse_block_title(raw_title)
		self.assertEqual(parsed_title.lexer, "C++")
		self.assertEqual(parsed_title.name, "Change stuff")
		self.assertEqual(parsed_title.options, {('INSERT AFTER', "bla", "hey, there is a comma and a parenthese ), how nice?")})

		raw_title = r'Change stuff again (insert in {{foo}} before "there are \"escaped\" things", hidden)'
		parsed_title = parse_block_title(raw_title)
		self.assertIsNone(parsed_title.lexer)
		self.assertEqual(parsed_title.name, "Change stuff again")
		self.assertEqual(parsed_title.options, {'HIDDEN', ('INSERT BEFORE', "foo", 'there are "escaped" things')})

class TestLitConfig(TestCase):
	def test_parser(self):
		"""
		Check that it is not possible to define multiple parents for the same
		tangle root.
		"""
		source = """
		```{lit-config}
		:tangle-root: foo
		:parent: bar
		```

		```{lit-config}
		:tangle-root: foo
		:parent: baz
		```
		"""
		# TODO: process this source and check that it leads to an exception

if __name__ == "__main__":
	main()
