var throttle = function(func, wait) {
  var lastExecutionTime = 0;
  var timeoutId;

  var throttledFunction = function(...args) {
    var currentTime = new Date().getTime();
    var timeSinceLastExecution = currentTime - lastExecutionTime;

    if (!timeoutId) {
      if (timeSinceLastExecution >= wait) {
        lastExecutionTime = currentTime;
        func(...args);
      } else {
        timeoutId = setTimeout(() => {
          lastExecutionTime = new Date().getTime();
          func(...args);
          timeoutId = null;
        }, wait - timeSinceLastExecution);
      }
    }
  };

  return throttledFunction;
};

var add = function(a, b) {
  console.log(a + b);
  return a + b;
}

var throttleAdd = throttle(add, 3000);

throttleAdd(10, 5);
throttleAdd(10, 2);
throttleAdd(5, 2);
