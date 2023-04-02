Reference documentation
=======================

Block title
-----------

The title of a literate block is structured as follows:

```
Language, The full title (some, option)
```

This means that the language parser is "Language", the reference name of the block is "The full title" and it has options 'SOME' and 'OPTION'. Valid options are:

 - **APPEND** Add the content of this block to the previous blocks with the same name
 - **REPLACE** Replace the content of this block

Append and replace require that the block has already been defined, and only work within the same document for now.

When the block name starts with "file:", the block is considered as the root
and the remaining of the name is the path of the file into which the tangled
content must be saved, relative to the root tangle directory.

Reference to a block
--------------------

```
{{The title of the referenced block (some, option)}}
```

Possible options are:

 - **HIDDEN** To hide the line where the reference (unless the "show hidden" option is turned on). This is used to avoid extra reading clutter while still ensuring the completeness of the code.

The syntax for referencing other code blocks is `{{Some block name}}` by default, but as this may conflict with the syntax of your programming language, you can customize it with the config options `lit_begin_ref` and `lit_end_ref`.

Local setup
-----------

The `lit-setup` directive can be used to setup local options.

 - **tangle-root** The same sphinx documentation can tangle multiple source trees. This sets the root of all files defined later in the file. Two literate blocks defined in different roots can have the same name.

 - **parent** The tangle root from which this one inherits.

For instance:

````
```{lit-setup}
:tangle-root: incremental-demo
```
````

Inheritance
-----------

When a tangle root inherit from another one (i.e., this other one is set as its parent), it can reference previously defined blocks:

````
```{lit-setup}
:tangle-root: versionA
```

```{lit} A block
foo
```

```{lit} Another block
bar
{{A block}}
```
````

````
```{lit-setup}
:tangle-root: versionB
:parent: versionA
```

```{lit} Result block
{{A block}}
{{Another block}}
```
````

Tangling `Result block` gives:

```
foo
bar
foo
```

When defining a block in a child tangle root with the same name as a block previously defined in the parent, it does not change the content of parent tangling, unless they use modifier options like 'replace' and 'append':

````
```{lit-setup}
:tangle-root: versionC
:parent: versionA
```

```{lit} A block (replace)
new foo
```

```{lit} Result block
{{A block}}
{{Another block}}
```
````

Tangling `Result block` gives:

```
new foo
bar
foo
```

See [Incremental demo](incremental-demo/index) for a live demo.
