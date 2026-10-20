var carlike = function(obj, loc) {
  obj.loc = loc;
  obj.move = move;
  return obj;
};
var move = function() {
  this.loc++;
}
var amy = carlike({}, 1);
amy.move();
var ben = carlike({}, 9);
ben.move();

setTimeout(ben.move, 1000);

//
console.log('---');
var carlike = function(obj, loc) {
  obj.loc = loc;
  obj.move = function() {obj.loc++;};
  return obj;
};

var amy = carlike({}, 1);
amy.move();
var ben = carlike({}, 9);
ben.move();

setTimeout(ben.move, 1000);



