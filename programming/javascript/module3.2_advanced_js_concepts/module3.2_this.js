var fn = function(a, b) {
  console.log(this);
};

fn(1, 2);

var ob = {method: fn};
var ob2 = {method: fn, tag: 2};
var ob3 = {method3: fn, tag: 3};
ob.method(1, 2);
ob2.method(1, 2);

console.log('1: ---');
// when this appears between the curly braces of an object:

var ob = {
  fn: function(a, b) {
    console.log(this);
  },
  tag: 0
};

ob.fn(1, 2);
var ob2 = {method: ob.fn, tag: 2};
ob2.method(1, 2);

console.log('2: ---');

var fn = function(one, two) {
  console.log(this, one, two);
};

var r={val: 'r'}, g={val: 'g'}, b={val: 'b'}, y={val: 'y'};
r.method = fn;
r.method(g, b);
fn(g, b);
fn.call(r, g, b);
r.method.call(y, g, b);

setTimeout(fn, 1000);
setTimeout(r.method, 1000);
setTimeout(function() {
  r.method();
}, 1000);

console.log('new ---')
console.log(this);
new r.method(g, b);
console.log('new ---')

