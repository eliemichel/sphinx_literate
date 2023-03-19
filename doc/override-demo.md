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

*Document B*

```{lit-setup}
:tangle-root: versionB
:parent: versionA
```

```{lit} Result block
{{A block}}
{{Another block}}
```

Tangled:

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

```{lit} A block (replace)
new foo
```

```{lit} Result block
{{A block}}
{{Another block}}
```

Tangled:

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

```{lit} Result block
{{A block}}
{{Another block}}
```

Tangled:

```{tangle} Result block
```

Expected:

```
foo
more foo
bar
foo
```
