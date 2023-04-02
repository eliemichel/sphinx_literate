Insert
======

```{lit-setup}
:tangle-root: demo/insert
```

It is possible to insert a block into a previously defined one.

````
```{lit} CMake, file:CMakeLists.txt
cmake_minimum_version()
project(foo)

add_executable(App main.cpp)
```

```{lit} CMake, Add deps (insert in {{file:CMakeLists.txt}} after "project(")
add_subdirectory(glfw)
```
````

```{lit} CMake, file:CMakeLists.txt
cmake_minimum_version()
project(foo)

add_executable(App main.cpp)
```

```{lit} CMake, Add deps (insert in {{file:CMakeLists.txt}} after "project(")
add_subdirectory(glfw)
```

```{lit} CMake, Add deps (append)
add_subdirectory(webgpu)
```

Tangled result
--------------

```{tangle} file:CMakeLists.txt
```

```{lit-registry}
```
