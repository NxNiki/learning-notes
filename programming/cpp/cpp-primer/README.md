# Cpp Primer_Notes
notes of book C++ Primer

## compiling a C++ program:
By default, the command to run the GNU compiler is g++:

`g++ -o prog1 prog1.cc`

The -o prog1 is an argument to the compiler and names the file in which to put the executable file. This command generates an executable file named prog1 or prog1.exe, depending on the operating system. Compilers usually include options to generate warnings about problematic constructs. It is usually a good idea to use these options. Our preference is to use -Wall with the GNU compiler, and to use /W4 with the Microsoft compilers.

## section 1.4
When we enter input to a program from the keyboard, different operating systems use different conventions to allow us to indicate end-of-file. On Windows systems we enter an end-of-file by typing a control-z—hold down the Ctrl key and press z— followed by hitting either the Enter or Return key. On UNIX systems, including on Mac OS X machines, end-of-file is usually control-d.

### section 1.5.1
Every class defines a type. The type name is the same as the name of the class.
the class author determines all the operations that can be used on objects of the class type.

Most operating systems support ﬁle redirection, which lets us associate a
named ﬁle with the standard input and the standard output:

`$ addItems <infile >outfile`

Assuming $ is the system prompt and our addition program has been compiled into an executable ﬁle named addItems.exe (or addItems on UNIX systems), this command will read transactions from a ﬁle named infile and write its output to a ﬁle
named outfile in the current directory.

## Section 2.1 Primitive Built-in Types
A char is guaranteed big enough to hold numeric values corresponding to the characters in the machine’s basic character set. A char is the same size as a machine byte (8 bits).

- Use an unsigned type when you know the values cannot be negative.
- Use int for integer arithmetic. short is usually too small, and in practice, long often has the same size as int. If your data values are larger than the minimum guaranteed size of an int, then use long long.
- Do not use plain char or bool in arithmetic expressions. Use them only to hold characters or truth values. Computations using char are especially problematic because char is signed on some machines and unsigned on others. If you
need a tiny integer, explicitly specify either a signed char or an unsigned char.
- Use double for floating-point computations; float usually does not have enough precision, and the cost of double-precision calculations versus single-precision is negligible. In fact, on some machines, double-precision operations are faster than single. The precision offered by long double is usually unnecessary and often entails considerable run-time cost.

### section 2.1.2 Type conversations
- If we assign an out-of-range value to an object of unsigned type, the result is the remainder of the value modulo the number of values the target type can hold.
  an 8-bit unsigned char can hold values from 0 through 255, inclusive. If we assign a value outside this range, the compiler assigns the remainder of that value modulo 256. Therefore, assigning –1 to an 8-bit unsigned char gives that object the value 255.

- If we assign an out-of-range value to an object of signed type, the result is undefined. The program might appear to work, it might crash, or it might produce garbage values.
Undefined behavior results from errors that the compiler is not required (and sometimes cannot) to detect. Even if the code compiles, a program that executes an undefined expression is in error.
Programs should usually avoid implementation-defined behavior, such as assuming that the size of an int is a fixed and known value. Such programs are said to be nonportable.

Converting an int to unsigned executes the same way as if we assigned the int to an unsigned:

```C++
unsigned u = 10;
int i = -42;
std::cout << i + i << std::endl; // prints -84
std::cout << u + i << std::endl; // if 32-bit ints, prints 4294967264
```

Converting a negative number to unsigned behaves exactly as if we had attempted to assign that negative value to an unsigned object.
The value “wraps around” as described above.

Writing `endl` has the effect of ending the current line and flushing the buffer
associated with that device.

```C++
unsigned u1 = 42, u2 = 10;
std::cout << u1 - u2 << std::endl; // ok: result is 32
std::cout << u2 - u1 << std::endl; // ok: but the result will wrap around
```

Expressions that mix signed and unsigned values can yield surprising results when the signed value is negative. It is essential to remember that signed values are automatically converted to unsigned.

```C++
unsigned a = 1;
int b = -1;
std::cout << a * b << std::endl; // ok: but the result will wrap around
```

### section 2.1.3 Literal

A value, such as 42, is known as a literal because its value is self-evident. Every literal has a type. The form and value of a literal determine its type.

```C++
20 /* decimal */
024 /* octal */
0x14 /* hexadecimal */
```

By default, decimal literals are signed.
Octal and hexadecimal literals can be either signed or unsigned types.

Character and Character String Literals:

```C++
’a’ // character literal
"Hello World!" // string literal
```

The type of a string literal is an array of constant chars. The compiler appends a null character (’\0’) to every string literal. Thus, the actual size of a string literal is one more than its apparent size.

```C++
\n // newline
\v // vertical tab
\\ // backslash
\r // carriage return


\t // horizontal tab
\b // backspace
\? // question mark
\f // formfeed

\a // alert (bell)
\" // double quote
\' // single quote
```

Specifying the Type of a Literal: 
```
L’a’ // wide character literal, type is wchar_t
u8"hi!" // utf-8 string literal (utf-8 encodes a Unicode character in 8 bits)
42ULL // unsigned integer literal, type is unsigned long long
1E-3F // single-precision floating-point literal, type is float
3.14159L // extended-precision floating-point literal, type is long double
```

## 2.2 Variables

### Variable Definitions
```C++
// ok: price is defined and initialized before it is used to initialize discount
double price = 109.99, discount = price * 0.16;
// ok: call applyDiscount and use the return value to initialize salePrice
double salePrice = applyDiscount(price, discount);
```
initialization and assignment are different operations in C++.

List Initialization:
```C++
int units_sold = 0;
int units_sold = {0};
int units_sold{0};
int units_sold(0);
```

The compiler will not let us list initialize variables of built-in
type if the initializer might lead to the loss of information
```C++
long double ld = 3.1415926536;
int a{ld}, b = {ld}; // error: narrowing conversion required
int c(ld), d = ld; // ok: but value will be truncated
```

Default Initialization:

Variables defined outside any function body are initialized to zero.

variables of built-in type defined inside a function are uninitialized. 
The value of an uninitialized variable of built-in type is undefined.
It is an error to copy or otherwise try to access the value of a variable whose value is undefined.


### section 2.2.2 Variable Declarations and Definitions
A declaration makes a name known to the program. A file that wants
to use a name defined elsewhere includes a declaration for that name. A definition
creates the associated entity.

```
extern int i; // declares but does not define i
int j; // declares and defines j

// Any declaration that includes an explicit initializer is a definition. 
extern double pi = 3.1416; // definition, doing so overrides the extern
```
Variables must be defined exactly once but can be declared many times.


## Section 2.3 Compound Types:
### section 2.3.1 References:
A reference defines an alternative name for an object.

```C++
int ival = 1024;
int &refVal = ival; // refVal refers to (is another name for) ival
int &refVal2; // error: a reference must be initialized
```

When we define a reference, instead of copying the initializer’s value, we bind the reference to its initializer. Once initialized, a reference
remains bound to its initial object. There is no way to rebind a reference to refer to a different object.

```C++
refVal = 2; // assigns 2 to the object to which refVal refers, i.e., to ival
int ii = refVal; // same as ii = ival

// ok: refVal3 is bound to the object to which refVal is bound, i.e., to ival
int &refVal3 = refVal;
// initializes i from the value in the object to which refVal is bound
int i = refVal; // ok: initializes i to the same value as ival
```

Reference definition:
```C++
int i = 1024, i2 = 2048; // i and i2 are both int s
int &r = i, r2 = i2; // r is a reference bound to i ; r2 is an int
int i3 = 1024, &ri = i3; // i3 is an int ; ri is a reference bound to i3
int &r3 = i3, &r4 = i2;  // both r3 and r4 are references
```

```C++
int &refVal4 = 10; // error: initializer must be an object
double dval = 3.14;
int &refVal5 = dval; // error: initializer must be an int object
```

### section 2.3.2 Pointers

```C++
int *ip1, *ip2; // both ip1 and ip2 are pointers to int
double dp, *dp2; // dp2 is a pointer to double ; dp is a double
```

Taking the Address of an Object:

```C++
int ival = 42;
int *p = &ival; // p holds the address of ival ; p is a pointer to ival
```
Because references are not objects, they don’t have
addresses. Hence, we may not define a pointer to a reference.
With some exceptions, the types of the pointer and the object to which it points must match:

```C++
double dval;
double *pd = &dval; // ok: initializer is the address of a double
double *pd2 = pd;
// ok: initializer is a pointer to double
int *pi = pd; // error: types of pi and pd differ
pi = &dval;
// error: assigning the address of a double to a pointer to int
```

dereference operator accesses the object through the pointer:

```
int ival = 42;
int *p = &ival; // p holds the address of ival ; p is a pointer to ival
cout << *p; // * yields the object to which p points; prints 42

*p = 0;  // * yields the object; we assign a new value to ival through p
cout << *p; // prints 0
```

`&` and `*` , are used as both an operator in an expression and as part of a declaration. The context in which a symbol is used determines what the symbol means:
In declarations, & and * are used to form compound types. In expressions, these same symbols are used to denote an operator. It can be helpful to ignore appearances and think of them as if they were different symbols.

```C++
int i = 42;
int &r = i; // & follows a type and is part of a declaration; r is a reference
int *p; // * follows a type and is part of a declaration; p is a pointer
p = &i; // & is used in an expression as the address-of operator
*p = i; // * is used in an expression as the dereference operator
int &r2 = *p; // & is part of the declaration; * is the dereference operator
```

Null Pointers:

```C++
int *p1 = nullptr; // equivalent to int *p1 = 0;
int *p2 = 0; // directly initializes p2 from the literal constant 0
// must #include cstdlib
int *p3 = NULL; // equivalent to int *p3 = 0;

int zero = 0;
pi = zero;
// error: cannot assign an int to a pointer
```

As with any other uninitialized variable, what happens when we use an uninitialized pointer is undefined. Using an uninitialized pointer almost always results in a
run-time crash. However, debugging the resulting crashes can be surprisingly hard.
Under most compilers, when we use an uninitialized pointer, the bits in the memory in which the pointer resides are used as an address.

It can be hard to keep straight whether an assignment changes the pointer or
the object to which the pointer points.

```C++
pi = &ival; // value in pi is changed; pi now points to ival 
*pi = 0; // value in ival is changed; pi is unchanged
```

void * pointers:

The type void* is a special pointer type that can hold the address of any object.

```C++
double obj = 3.14, *pd = &obj;
// ok: void* can hold the address value of any data pointer type
void *pv = &obj; // obj can be an object of any type
pv = pd; // pv can hold a pointer to any type
```

a variable definition consists of a base type and a list of declarators.
Each declarator can relate its variable to the base type differently from the other
declarators in the same definition.

```C++
// i is an int ; p is a pointer to int ; r is a reference to int
int i = 1024, *p = &i, &r = i;

int* p1, p2; // p1 is a pointer to int ; p2 is an int
int *p1, *p2; // both p1 and p2 are pointers to int
```

Pointers to Pointers:

A pointer is an object in memory, so like any object, it has an address. Therefore, we can store
the address of a pointer in another pointer.

```C++
int ival = 1024;
int *pi = &ival;  // pi points to an int
int **ppi = &pi;  // ppi points to a pointer to an int

cout << "The value of ival\n"
<< "direct value: " << ival << "\n"
<< "indirect value: " << *pi << "\n"
<< "doubly indirect value: " << **ppi
<< endl;
```

References to Pointers:

```C++
int i = 42;
int *p;
// p is a pointer to int
int *&r = p; // r is a reference to the pointer p
r = &i; // r refers to a pointer; assigning &i to r makes p point to i
*r = 0; // dereferencing r yields i, the object to which p points; changes i to 0
```
The easiest way to understand the type of r is to read the definition right to left.
The symbol closest to the name of the variable (& in &r) is the one that has the most immediate effect on the variable’s type. Thus, we know that r is a reference. 
The next symbol, * in this case, says that the type r refers to is a pointer type. 
Finally, the base type of the declaration says that r is a reference to a pointer to an int.


## const Qualifier

const variables are defined as local to the file. When we define a const with the same
name in multiple files, it is as if we had written definitions for separate variables
in each file.

A const object after must be initialized in its definition.

```C++
const int bufSize = 512; // input buffer size

const int i = get_size(); // ok: initialized at run time
const int j = 42; // ok: initialized at compile time
const int k; // error: k is uninitialized const
```

To define a single instance of a const variable, we use the keyword extern
on both its definition and declaration(s):

```C++
// file_1.cc defines and initializes a const that is accessible to other files
extern const int bufSize = fcn();
// file_1.h
extern const int bufSize; // same bufSize as defined in file_1.cc
```

References to const:

```
const int ci = 1024;
const int &r1 = ci;  // ok: both reference and underlying object are const
r1 = 42;  // error: r1 is a reference to const
int &r2 = ci;  // error: non const reference to a const object
```

we can initialize a reference to const from any expression that can be
converted to the reference type.

```C++
int i = 42;
const int &r1 = i;  // we can bind a const int& to a plain int object
const int &r2 = 42; // ok: r2 is a reference to const
const int &r3 = r1 * 2; // ok: r3 is a reference to const
int &r4 = r1 * 2; // error: r4 is a plain, non const reference


double dval = 3.14;
const int &ri = dval;

// The above can be considered as:
const int temp = dval; // create a temporary const int from the double
const int &ri = temp;  // bind ri to that temporary
```

Pointers and const:

```C++
const double pi = 3.14; // pi is const ; its value may not be changed
double *ptr = &pi; // error: ptr is a plain pointer
const double *cptr = &pi; // ok: cptr may point to a double that is const
*cptr = 42; // error: cannot assign to *cptr
```

const Pointers:

The fact that a pointer is itself const says nothing about whether we can use
the pointer to change the underlying object.

```C++
int errNum = 0;
int *const curErr = &errNum;  // curErr will always point to errNumb

const double pi = 3.14;
const double *const pip = &pi;  // pip is a const pointer to a const object
```

Top-level const:

```C++
int i = 0;
int *const p1 = &i; // we can’t change the value of p1 ; const is top-level
const int ci = 42; // we cannot change ci ; const is top-level
const int *p2 = &ci; // we can change p2 ; const is low-level
const int *const p3 = p2; // right-most const is top-level, left-most is not
const int &r = ci; // const in reference types is always low-level
```
When we copy an object, top-level const is ignored.
Low-level const is never ignored.

### section 2.4.4 constexpr and Constant Expressions

A constant expression is an expression whose value cannot change and that can
be evaluated at compile time. 

```C++
const int max_files = 20; // max_files is a constant expression
const int limit = max_files + 1; // limit is a constant expression
int staff_size = 27; // staff_size is not a constant expression
const int sz = get_size(); // sz is not a constant expression
```

Under the new standard, we can ask the compiler to verify that a variable is a
constant expression by declaring the variable in a constexpr declaration.

```C++
constexpr int mf = 20;  // 20 is a constant expression
constexpr int limit = mf + 1;  // mf + 1 is a constant expression
constexpr int sz = size();  // ok only if size is a constexpr function
```

The types we can use in a constexpr are known as “literal types” because they are simple enough to have literal values.
the arithmetic, reference, and pointer types are literal types.

when we define a pointer in a constexpr declaration, the constexpr specifier applies to the pointer, not the type to which the pointer points:

```C++
const int *p = nullptr;  // p is a pointer to a const int
constexpr int *q = nullptr;  // q is a const pointer to int
```


### 2.5.1 Type Aliases

```C++
typedef double wages; // wages is a synonym for double
typedef wages base, *p; // base is a synonym for double, p for double*
```

alias declaration:

```C++
using SI = Sales_item;  // SI is a synonym for Sales_item
```

the following declarations use the type `pstring`, which is an alias for the type `char*`
```C++
typedef char *pstring;
const pstring cstr = 0; // cstr is a constant pointer to char
const pstring *ps; // ps is a pointer to a constant pointer to char
```

When we rewrite the declaration using `char*`, the base type is `char` and the `*` is part of the declarator. In this case,
`const char` is the base type.

```C++
const char *cstr = 0;  // wrong interpretation of const pstring cstr, this is a pointer to const char.
```

### 2.5.2 The `auto` type specifier

`auto` ignores top-level `const` and keeps low-level `const`:
```C++
const int ci = i, &cr = ci;
auto b = ci; // b is an int (top-level const in ci is dropped)
auto c = cr; // c is an int ( cr is an alias for ci whose const is top-level)
auto d = &i; // d is an int* ( & of an int object is int* )
auto e = &ci; // e is const int* ( & of a const object is low-level const )

const auto f = ci;  // deduced type of ci is int ; f has type const int

auto &g = ci;  // g is a const int& that is bound to ci
auto &h = 42;  // error: we can’t bind a plain reference to a literal
const auto &j = 42; // ok: we can bind a const reference to a literal

auto k = ci, &l = i; // k is int ; l is int&
auto &m = ci, *p = &ci; // m is a const int& ; p is a pointer to const int
// error: type deduced from i is int ; type deduced from &ci is const int
auto &n = i, *p2 = &ci;
```

### 2.5.3 The `decltype` Type specifier

The compiler gives `sum` the same type as the type that would be returned if we were to call `f`.

```C++
decltype(f()) sum = x;  // sum has whatever type f returns

const int ci = 0, &cj = ci;
decltype(ci) x = 0; // x has type const int
decltype(cj) y = x; // y has type const int& and is bound to x
decltype(cj) z;  // error: z is a reference and must be initialized


// decltype of an expression can be a reference type
int i = 42, *p = &i, &r = i;
decltype(r + 0) b; // ok: addition yields an int ; b is an (uninitialized) int
decltype(*p) c;  // error: c is int& and must be initialized (---why? isn't *p is int?)
```

when we dereference a pointer, we get the object to which the pointer points. Moreover, we can assign to
that object. Thus, the type deduced by decltype(*p) is int&, not plain int.

```C++
// decltype of a parenthesized variable is always a reference
decltype((i)) d;  // error: d is int& and must be initialized
decltype(i) e;  // ok: e is an (uninitialized) int
```
















