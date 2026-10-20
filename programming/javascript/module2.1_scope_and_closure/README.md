## Scope:

A scope (`lexical scope`) is a part of the program where binding between a variable and a value is valid.
It determines which variable can be written in the source code.

- Global scope
  The global scope is shared in some JS environments.

```JavaScript
var hero = aHero();
var newSaga = function() {
  var foil = aFoil();
}
newSaga();
console.log(foil) // this will not work
```

- A new lexical scope is created every time a function is defined.
  
```JavaScript
var hero = aHero();
var newSaga = function() {
  foil = aFoil();
}
newSaga();
console.log(foil) // this will work but not suggested.
```

- Unlike other programming languages, a new lexical scope is NOT created in `if` or `while` clause.

```JavaScript
var hero = aHero();
if ( checkSomething()) {
  var foil = aFoil();
}
console.log(foil) // this will work
```

```JavaScript
var hero = aHero();
if ( checkSomething()) {
  let foil = aFoil();
}
console.log(foil) // this will not work
```

## Execution context/in-memory scope:

- Execution context is the `in-memory scope` structures to store variables and their values when a program runs.
- It determines which variables are accessible during run time. (lexical scope determines where variable names can be written in the source code)
- A new execution context should be created every time you run a function.
- Execution context looks like a collection of key-value pairs (similar to but not objects).


## Contexts vs. Objects:

`this` cannot refer to a context. It is used as an object with keys matching the local variables, but no such thing exists.

Each variable in the global context has a corresponding property on the global object. In the browser, the global object is referred to as `window`:

```JavaScript
var global_variable = 7;
console.log(global_variable);
console.log(window.global_variable);

var gimmeTheGlobalScope = function() {
  return window;
};
```

## Closures:

A [closure](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures) is the combination of a function bundled together (enclosed) with references to its surrounding state (the lexical environment). In other words, a closure gives you access to an outer function's scope from an inner function. 

Check the execution context of this simulated snippet:
```JavaScript
var sagas = [];
var hero = aHero();
var newSaga = function() {
  var foil = aFoil();
  sagas.push(function() {
    var deed = aDeed();
    console.log(hero+foil+deed);
  });
});

newSaga();
sagas[0]();
sagas[0]();
newSaga();
sagas[0]();
sagas[1]();
```






