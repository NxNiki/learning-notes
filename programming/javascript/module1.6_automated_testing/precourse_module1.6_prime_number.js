
// this function does not give the right answer, still trying to figure out the reason...
var isPrime = function(n) {
  return Array.from({length: Math.floor(Math.sqrt(n))}, function(_, index) { return index + 2; })
    .every(function(i) { return n % i !== 0; });
};

console.log(Array.from({length: Math.floor(Math.sqrt(101))}, function(_, index) { return index + 2; }));
console.log(Array.from({length: Math.floor(Math.sqrt(104743))}, function(_, index) { return index + 2; })
  .every(function(i) {return 104743 % i !==0; })
);

function isPrime(number) {
  if (number < 2) {
    return false;
  }
  for (let i = 2; i <= Math.sqrt(number); i++) {
    if (number % i === 0) {
      return false;
    }
  }
  return true;
};

// console.log(isPrime(10));
// console.log(isPrime(13));

var count = 0;
var number = 1;
while (count < 10001) {
  number++;
  if (isPrime(number)) {
    count++;
    // console.log(count);
  }
}
console.log(number);


// function isPrime(number) {
//   if (number < 2) {
//     return false;
//   }
//   for (let i = 2; i <= Math.sqrt(number); i++) {
//     if (number % i === 0) {
//       return false;
//     }
//   }
//   return true;
// }

function findNthPrime(n) {
  let count = 0;
  let candidate = 2;

  while (count < n) {
    if (isPrime(candidate)) {
      count++;
    }
    candidate++;
  }

  return candidate - 1; // Subtract 1 to get the actual prime number
}

const ans = findNthPrime(10001);
console.log(ans);
