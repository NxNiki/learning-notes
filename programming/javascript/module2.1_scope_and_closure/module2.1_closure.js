
var makeStopWatch = function () {
  var elapsed = 0;
  var stopwatch = function() { return elapsed; };
  var increase = function() { elapsed++; };

  setInterval(increase, 1000);
  return stopwatch;
}

var stopwatch1 = makeStopWatch();
var stopwatch2 = makeStopWatch();

console.log(stopwatch1());
console.log(stopwatch2());