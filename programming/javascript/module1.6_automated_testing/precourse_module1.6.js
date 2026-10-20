array = new Array(10)
console.log(array.length)
array.length = 5
console.log(array.length)
console.log(array[4])


var array = ['peanut', 'butter', 'and', 'jelly'];
console.log(array.slice(0, 1))
console.log(array.slice(2, 2))
console.log(array.slice(3, 0))


var array = [1, 2];
array.unshift(3)
console.log(array)
array.shift()
console.log(array)


console.log(Array(5).join(' ' + 'Brain'))


var currentDate = new Date();
var currentYear = (currentDate.getFullYear());
console.log(currentYear)


var sum = 0;

for (var i = 1; i < 1000; i += 1) {
  if (i % 3 === 0 || i % 5 === 0) {
    sum += i;
  }
}
console.log(sum)


var sum = Array.from({ length: 999 }, function(_, index) {return index + 1;})
  .filter(function(number) {return number % 3 === 0 || number % 5 === 0;})
  .reduce(function(accumulator, currentValue) {return accumulator + currentValue;}, 0)
console.log(sum)


products = [
  { name: 'Sonoma', ingredients: ['artichoke', 'sundried tomatoes', 'mushrooms'], containsNuts: false },
  { name: 'Pizza Primavera', ingredients: ['roma', 'sundried tomatoes', 'goats cheese', 'rosemary'], containsNuts: false },
  { name: 'South Of The Border', ingredients: ['black beans', 'jalapenos', 'mushrooms'], containsNuts: false },
  { name: 'Blue Moon', ingredients: ['blue cheese', 'garlic', 'walnuts'], containsNuts: true },
  { name: 'Taste Of Athens', ingredients: ['spinach', 'kalamata olives', 'sesame seeds'], containsNuts: true }
];


var ingredientCount = { '{ingredient name}': 0 };

// for (var i = 0; i < products.length; i += 1) {
//   for (var j = 0; j < products[i].ingredients.length; j += 1) {
//     ingredientCount[products[i].ingredients[j]] = (ingredientCount[products[i].ingredients[j]] || 0) + 1;
//   }
// }

// ingredients = products.map(function(product) { return product.ingredients; }).flat();

ingredientCount = products.map(function(product) { return product.ingredients; }).flat().reduce(function (counter, currentValue) {
  counter[currentValue] = (counter[currentValue] || 0) + 1;
  return counter;
}, ingredientCount);
console.log(ingredientCount);


array = [1, 2, 3, 4, 1, 2, 3, 1, 2, 1];

const countOccurrences = array.reduce(function (accumulator, currentValue) {
  // If the current value is not in the accumulator, initialize its count to 1
  accumulator[currentValue] = (accumulator[currentValue] || 0) + 1;
  return accumulator;
}, {});

console.log(countOccurrences);
// Output: {1: 4, 2: 3, 3: 2, 4: 1}



var isPalindrome = function(number) {
  return number.toString() === number.toString().split('').reverse().join('');
};

var largestPalindrome = 0;
for (var i = 999; i > 100; i--) {
  for (var j = i; j > 100; j--) {
    if (i * j < largestPalindrome) {
      break;
    }
    if (isPalindrome(i * j)) {
      largestPalindrome = i * j;
    }
  }
}
console.log(largestPalindrome);


var divisors = Array.from({length: 20}, function(_, index) { return index + 1; });
var isValid = function(number) {
  return divisors.every(function(divisor) {
    return number % divisor === 0;
  });
};

var start = 20;
var smallestNumber;
while (true) {
  if (isValid(start)) {
    smallestNumber = start;
    break;
  }
  start += 20;
}

console.log(smallestNumber)


//

function gcd(a, b) {
  return b === 0 ? a : gcd(b, a % b);
}

function lcm(a, b) {
  return (a * b) / gcd(a, b);
}

function smallestMultiple() {
  let multiple = 1;

  for (let i = 2; i <= 20; i++) {
    multiple = lcm(multiple, i);
  }

  return multiple;
}

const result = smallestMultiple();
console.log(result);


var gcd = function(a, b) {
  return b === 0 ? a : gcd(b, a % b);
};

var lcm = function(a, b) {
  return (a * b) / gcd(a, b);
};

var leastCommonMultiple = Array.from({length: 20}, function(_, index) { return index + 1; })
  .reduce(function(multiple, val) { return lcm(multiple, val); }, 1);

console.log(leastCommonMultiple);


var array = [1, 3, 4, 3, 2, 5, 6, 9];

// var sumOfSquares = array.map(function(x) { return x ** 2; }).reduce(function(x, y) { return x + y; }, 0);
// var sumOfSquares = array.reduce(function(x, y) { return x + y ** 2; }, 0);
// var squareOfSums = array.reduce(function(x, y) { return x + y; }, 0) ** 2;

var sumOfSquares = array.reduce(function(x, y) { return x + Math.pow(y, 2); }, 0);
var squareOfSums = Math.pow(array.reduce(function(x, y) { return x + y; }, 0), 2);

var difference = sumOfSquares - squareOfSums;
console.log(difference);
console.log(array.map(function(x) { return x ** 2; }));


