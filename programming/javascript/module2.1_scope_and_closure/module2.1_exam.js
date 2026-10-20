
// Q1:
var x = 30;

function get (x) { return x; }
function set (value) { x = value; }

set(10);
var result = get(20);

console.log(result); // comment the remaining code to get correct answer.

// Q2:
var x = 30;

function get () { return x; }
function set (value) { x = value; }

set(10);
var result = get(20);

console.log(result);

// Q3:
var x = 10;

function outer () {
  x = 20;
  function inner () {
    var x = x + 20;
    return x;
  }
  inner();
}

outer();

var result = x;

console.log(result);

// Q4:
var x = 10;

function add (y) {
  return x + y;
}

function strangeAdd (x) {
  return add(x) + add(x);
}

var result = strangeAdd(5);

console.log(result);

// Q5:
var myArray = [2, 3, 4, 5];
function doStuff(arr) {
  arr = [];
}

doStuff(myArray);

console.log(myArray);
