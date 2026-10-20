# problem solving:

1. interpret the prompt
2. IOCE (input, output, constraints, edge case)
3. write tests
4. high level strategy (make a diagram)
5. pseudocode the strategy
6. implement the solution

IOCE stands for the input, output, constraints, and edge cases in a problem. 
Strategy is some high-level steps you think of to solve the problem. 
Write tests help us understand the problem better by clarifying the input and expected output. 
Pseudocode helps clarify the steps to solve the problem independent of the programming language details. 
Code is the exact code to implement the algorithm. 
Refactor further improves the code for readability, efficiency, and etc.

note: readability is important to your productivity, as it may take several rounds of reviews before your pull request is accepted. 

install packages with npm and update the package.json file:

```
npm install --save underscore
```

use `npm install` to update the packages.

## IIFE (immediately invoked function expression):

In module 1.6 testBuilder, we need IIFE to run tests successfully:

```Javascript
var should = chai.should();
var randomDigits = Math.floor(Math.random() * Math.pow(10, 20)).toString();

for (var prefix = 622126; prefix <= 622925; prefix++) {
  var prefix = prefix.toString();
  for (var length = 16; length <= 19; length++) {
    var cardNumber = prefix + randomDigits.slice(0, length - prefix.length);
    (function(currentCardNumber) {
      it('as a prefix of ' + prefix + ' and a length of ' + length, function () {
        detectNetwork(currentCardNumber).should.equal('China UnionPay');
      });
    })(cardNumber);
  }
}
```







