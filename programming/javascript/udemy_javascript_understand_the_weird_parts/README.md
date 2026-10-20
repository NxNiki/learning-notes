- Section 2:

  - module 7: Conceptual Aside:

    - Syntax parsers
    - Lexical environments
    - Execution contexts

  - module 8: name value pair and objects:

    - object: a collection of name/value pairs. (unlike other programming languages that may have more complex concepts)

  - module 10: The global environment and global object:

    - The base execution context is the global execution context.
    - It creates a global object.
    - It also creates a special variable `this`.
    - The `window` object (current window in the browser) is the current global object inside browsers.
    - At global level, the variable `this` and the object `window` are equal (if the code is run in a browser).
    - There is always a global object when you run JS.

    - Global: not inside a function.
      When you create variables and functions that not inside a function, they are attached to the global object.

    - When code is executed, an `execution context` is created.
      - global object (`window` if run in browser)
      - `this` (equal to `window` if run in browser)
      - Outer environment
      - Your code (not inside a function)









