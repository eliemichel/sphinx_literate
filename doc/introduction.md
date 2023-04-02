Introduction
============

```{lit-setup}
:tangle-root: Introduction
```

*sphinx_literate* is an extension inspired by the concept of **Literate Programming**.

It provides a *directive* called `lit`, which is close to Sphinx' native code block directive, except that the author can **specify how these literate code blocks should be assembled together** in order to produce the full code that is presented in the documentation.

This literate code block provides 2 complementary features:

 1. The documentation's source code can be transformed into a **fully working
    code**. This is traditionally called the **tangled** code.

 2. The documentation can display links that **help navigating** through the code
    even though the documentation presents it non-linearly.

Simple example
--------------

### Source

Let's take a very simple example. The following snippet in the documentation's source defines a first `lit` block:

````
```{lit} Base skeleton
#include <iostream>
int main(int, char**) {
    {{Main content}}
}
```
````

```{note}
I am using [MyST](https://myst-parser.readthedocs.io/en/latest/) syntax instead of Sphinx' default ReST.
```

There are **two key differences** with a usual code block:

 1. A `lit` block always has a **name**, e.g., *"Base skeleton"*.
 2. The content of a `lit` block can contain **references** like in this case `{{Main content}}`, which points to the block whose name is *"Main content"*, whenever this will be defined.

```{important}
There is **no need** for the referenced block *"Main content"* **to be already defined**. The natural order in which things are introduced in a literate program is often not the same as the order in which a program is written.
```

```{note}
A block name can include spaces, but it must not include comma `,` nor parentheses `(`.
```

And we can later define the main content, in another `lit` block.

````
```{lit} C++, Main content
std::cout << "Hello world" << std::endl;
```
````

One addition here is the **language for syntax highlight**: `C++` is specified before the name, separated from the block name by a comma. This is optional.

### HTML Result

When building the HTML documentation as usual with `make html`, this block is compiled into the following:

```{lit} C++, Base skeleton
#include <iostream>
int main(int, char**) {
    {{Main content}}
}
```

```{lit} C++, Main content
std::cout << "Hello world" << std::endl;
```

You can see that the reference to *Main content* in the first block is replaced by a navigation link that references the second block.

Depending on the "literate options" that you set, you may see each block's name in its lower-right corner, as well as links to where it is referenced and modified.

```{figure} /doc/images/literate-options-dark.png
:align: center
:class: with-shadow
The literate options, located in the right-hand panel.
```

```{note}
The literate options buttons have only been tested with the [Furo](https://github.com/pradyunsg/furo) Sphinx theme, this may require some adaptation for other themes.
```

### Tangled Result

This extension adds a new builder, called **tangling**. You can call it with:

```
make tangle
```

This will create in `_build/tangle` a hierarchy of files from the content of the documentation. This only looks at blocks whose name starts with "file:" to create files. Let us then add an extra `lit` block:

````
```{lit} C++, file:main.cpp
{{Base skeleton}}
```
````

```{lit} C++, file:main.cpp
{{Base skeleton}}
```

When tangling, you can see a file `main.cpp` in the tangle directory. It is also possible to display the tangled result directly in the documentation using the `tangle` directive:

````
```{tangle} Base skeleton
```
````

```{tangle} Base skeleton
```
