// calling a function twice creates two different objects:
// similarly, two execution context created by the same function are different.

var makeArray = function() {
  return [];
}

var array1 = makeArray();
var array2 = makeArray();

console.log(array1 === array2);