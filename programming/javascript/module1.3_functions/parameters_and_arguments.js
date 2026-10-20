// parameter list:

var fun = function (input) {
  console.log(input.toUpperCase());
}


// argument:
fun('Hi');


// dynamic argument lists:
var fun = function(input) {
  console.log(arguments);
};

fun('hello');
fun('hello', 3);

var fun = function(input, in2, in3) {
  console.log(arguments[0], in2);
}
fun('hello', 2);


// inner argument variable masks the outer one:
var fun = function(input) {
  console.log(arguments);
  var innerFun = function(input) {
    console.log(arguments);
  };
  innerFun('yo')
};

fun('hi');


// passing function to functions:
var fun = function(input) {
  console.log(input.toUpperCase());
}

// wrap desired behavior in an anonymous function:
setTimeout(
  function() {fun('hi');}, 1000
);

// exercise:
var myFunc = function(arg1) {
  console.log(arg1)
  var argument2 = arg1;
  return argument2;
}
myFunc('second argument', 'third argument', 'first argument');


var myFunc = function(myStr) {
  console.log('lamp shade');
  return myStr;
}

// setTimeout(myFunc('Hello World'), 1500);


var myFunc = function(myStr) {
  console.log(myStr);
  return myStr;
}

setTimeout(myFunc, 1500);


var myFunc = function(myStr) {
  console.log(myStr);
  return myStr;
}

setTimeout(function(timeoutArgument) {
  myFunc('Hello World')
}, 1500);


var listAllShirts = function(inventory) {

  var res = [];
  var shirts = inventory['shirts'];
  for (var i = 0; i < shirts.length; i++) {
      res.push(`${shirts[i]['designer']} ${shirts[i]['name']} ${shirts[i]['price']}`);
  }
  return res;
};