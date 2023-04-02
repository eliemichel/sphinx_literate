Insert
======

```{lit-setup}
:tangle-root: demo/insert
```

It is possible to insert a block into a previously defined one.

```{lit} CMake, file:CMakeLists.txt
cmake_minimum_version()
project(foo)

add_executable(App main.cpp)
```

```{lit} CMake, Add deps (insert in {{file:CMakeLists.txt}} after "project(")
add_subdirectory(glfw)
```

Tangled result
--------------

*Including content from the previous page.*

```{tangle} file:CMakeLists.txt
```
