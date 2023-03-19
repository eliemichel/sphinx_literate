Override demo
=============

We test it inheritance override system.

*Document A*

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

```{lit} Result block
{{A block}}
{{Another block}}
```

*Document B*

```{lit-setup}
:tangle-root: versionB
:parent: versionA
```

```{lit} Result block
{{A block}}
{{Another block}}
```

```{tangle} Result block
```

Expected:

```
foo
bar
foo
```

*Document C*

```{lit-setup}
:tangle-root: versionC
:parent: versionA
```

```{lit} A block
new foo
```

```{lit} Result block
{{A block}}
{{Another block}}
```

```{tangle} Result block
```

Expected:

```
new foo
bar
foo
```

*Document D*

```{lit-setup}
:tangle-root: versionD
:parent: versionA
```

```{lit} A block (append)
more foo
```

```{tangle} Result block
```

Expected:

```
foo
more foo
bar
foo
more foo
```

Inherit from grand-parents
--------------------------

### Grand-parent

```{lit-setup}
:tangle-root: grand-parent
```

```{lit} Some foo
grand-parent's foo
```

```{lit} Some bar
grand-parent's bar
```

```{lit} Some baz
grand-parent's baz
```

```{lit} Result
{{Some foo}}
{{Some bar}}
{{Some baz}}
```

```{tangle} Result
```

### Parent

```{lit-setup}
:tangle-root: parent
:parent: grand-parent
```

```{lit} Some bar
parent's bar
```

```{tangle} Result
```

### Child

```{lit-setup}
:tangle-root: child
:parent: parent
```

```{lit} Some foo (replace)
child's foo
```

```{lit} Some bar (replace)
child's bar (replaces the parent but not affecting the grand-parent)
```

```{lit} Some baz (append)
child's baz
```

```{tangle} Result
```

*Expected*

```
child's foo
grand-parent's bar
grand-parent's baz
child's baz
```

