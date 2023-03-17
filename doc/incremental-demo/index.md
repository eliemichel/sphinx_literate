Incremental demo
================

```{lit-setup}
:tangle-root: incremental-demo
```

`sphinx_literate` can create diff from one page to another one. This section of the doc demo this feature.

Create a simple hello world:

```{lit} file: main.cpp
#include <iostream>

int main (int, char**) {
    std::cout << "Hello, world!" << std::endl;
    return 0;
}
```

In `CMakeLists`, me create our main target:

```{lit} Define target
add_executable(App main.pp)
```

Add the header:

```{lit} file: CMakeLists.txt
cmake_minimum_required(VERSION 3.0...3.25)
project(
	LearnWebGPU # name of the project, which will also be the name of the visual studio solution if you use it
	VERSION 0.1.0 # any version number
	LANGUAGES CXX C # programming languages used by the project
)

{{Define target}}
{{Recommended extras}}
```

```{lit} Recommended extras
set_target_properties(App PROPERTIES
	CXX_STANDARD 17
	COMPILE_WARNING_AS_ERROR ON
)
```

```{lit} Recommended extras (append)
if (MSVC)
	target_compile_options(App PRIVATE /W4)
else()
	target_compile_options(App PRIVATE -Wall -Wextra -pedantic)
endif()
```
