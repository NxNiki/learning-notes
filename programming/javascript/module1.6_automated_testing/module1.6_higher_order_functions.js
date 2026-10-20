var numbers = [1, 2, 3];
var msg = '';
var isEven = function(item) {
  msg += (item % 2) === 0;
};

(numbers).forEach(isEven);

console.log(msg);
console.log(numbers);