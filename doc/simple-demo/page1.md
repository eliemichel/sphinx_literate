Page 1
======

Source
------

This is a test for the literate programming sphinx extension developped for this guide.

```{lit} C++, file: src/main.cpp
#include <iostream>
{{Includes}}

int main(int, char**) {
    {{Main content}}
}
```

Before anything, let's talk about the return value:

```{lit} C++, Main return
:caption: Main return

return EXIT_SUCCESS;
```

Note that this requires to include the `cstdlib` header:

```{lit} Includes
#include <cstdlib>
```

Then we can focus on the core content:

```{lit} Main content
std::cout << "Hello world" << std::endl;
{{Main return}}
```

```{lit} CMake, file: CMakeLists.txt
:emphasize-lines: 2, 3
project(Example)
add_executable(
    App
    {{Source files}}
)
```

```{lit} Source files
src/main.cpp
```

Tangled result
--------------

```{tangle} file: src/main.cpp
```

```{tangle} file: CMakeLists.txt
```
