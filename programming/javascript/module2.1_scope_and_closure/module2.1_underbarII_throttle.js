// var currentTime = new Date().getTime();
// console.log(currentTime);


var throttle = function(func, wait) {
  var previousExecutionTime = 0;
  var result;
  var timeoutId;

  var funcWrapper = function(...args) {
    previousExecutionTime = new Date().getTime();;
    result = func.apply(this, args);
  }

  var throttleFun = function(...args) {
    var currentTime = new Date().getTime();
    var remainingWait = wait - (currentTime - previousExecutionTime);

    if (remainingWait <= 0) {
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
      funcWrapper(...args);
    } else {
      if (!timeoutId) {
        timeoutId = setTimeout(funcWrapper, remainingWait, ...args);
      }
    }

    return result;
  };

  return throttleFun;
};

var add = function(a, b) {
  console.log(a + b)
  return a + b;
}

throttleAdd = throttle(add, 3000);
throttleAdd(10, 5)
throttleAdd(10, 2)
throttleAdd(5, 2)
