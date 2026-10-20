
// One interested thing in javascript is a function can work with more arguments than
// the number of parameters in the function definition:

var fun1 = function(val) {
  return val + 2;
}

console.log(fun1(10, 12));


// define a function that is negative of another function:
var test = function(val) {
  return val > 10;
}

var negTest = function(val, testFun) { return !testFun(val) };
console.log(negTest(20, test));

// or don't include test in the parameter list:
var negTest2 = function(val) { return !test(val) };
console.log(negTest2(20));
