Page 2
======

```{lit-setup}
:tangle-root: incremental-demo-p2
:parent: incremental-demo-p1
```

We now bring updates to the previous tangle root, by marking `incremental-demo-p1` as the parent of our current tangle:

````
```{lit-setup}
:tangle-root: incremental-demo-p2
:parent: incremental-demo-p1
```
````

```{warning}
The same tangle root cannot have multiple parents!
```

For instance, we add a new source file:

```{lit} CMake, Define target (replace)
add_executable(App main.cpp foo.h foo.cpp)
```

Tangled
-------

```{tangle} CMake, file: CMakeLists.txt
```

We can also tangle only the diff wrt. the previous version:

````
TODO
```{tangle} CMake, file: CMakeLists.txt
:diff:
```
````
