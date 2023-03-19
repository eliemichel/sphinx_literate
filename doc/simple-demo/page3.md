Page 3
======

Multi-page source
-----------------

We define some part of the code here:

```{lit} C++, Main body
int x = 10;
int y = 32;
{{Add x and y into z}}
std::cout << "z = " << z << std::endl;
```

```{lit} C++, file: src/main2.cpp
#include <iostream>
int main(int, char**) {
    {{Main body}}
    return 0;
}
```

Tangled result
--------------

*Including content from the previous page.*

```{tangle} file: src/main2.cpp
```
