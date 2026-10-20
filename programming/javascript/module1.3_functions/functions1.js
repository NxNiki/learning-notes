var fun = function(){};

fun['x'] = 9;
fun[ 0 ] = 'cat';
fun[ 1 ] = 'dog';

console.log(fun['x'])
for (x in fun) {
  console.log(fun[x]);
}

// the only special power functions is that they can be invoked (run).
// to activate whatever behavior that function is coded to do.

var fun = function () {console.log(2)};

// immediate invocation of a function:
// the first parentheses represent parameter list,
// the second request function invocation.
var res = function() {return 1;} ();


// adding parentheses after fuction defintion discards the function but returns a value of the function:
var fun = function () {return 1;} ();
console.log(fun);

