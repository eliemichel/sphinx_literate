Hidden
======

```{lit-setup}
:tangle-root: demo/hidden
```

It is possible to add a block without showing it, for implementation details that would not interest the reader so much (they can still see them by enabling it in options).

````
```{lit} file:test.txt
To: You
From: Me
Body:
  {{Body (hidden)}}
```

```{lit} Body (hidden)
This is the message!
Note btw how when it spans on several lines the indentation
from the parent reference is propagated to all lines.

Regards,
{{Signature}}
```

```{lit} Signature
Me
```
````

HTML result
-----------

```{lit} file:test.txt
To: You
From: Me
Body:
  {{Body (hidden)}}
```

```{lit} Body (hidden)
This is the message!
Note btw how when it spans on several lines the indentation
from the parent reference is propagated to all lines.

{{Signature}}
```

```{lit} Signature
Regards,
Me
```

Tangled result
--------------

```{tangle} file:test.txt
```
