// This explain the issue:
/*

Assignment:
Testbuilder - Writing tests for China UnionPay.

Issue:
As there are too many test cases, I wrote the following snippet to generate cardNumber and to the test:

for (var prefix = 624; prefix <= 626; prefix++) {
    var prefix = prefix.toString();
    for (var length = 16; length <= 19; length++) {
      it('as a prefix of ' + prefix + ' and a length of ' + length, function () {
        detectNetwork(prefix + randomDigits.slice(0, length - prefix.length)).should.equal('China UnionPay');
      });
    }
  }
The above code results error:
TypeError: Cannot read properties of undefined (reading 'should')
    at Context.<anonymous> (detectNetwork.test.js:325:78)

Actions taken:
However it works when I assign the card number in a variable like this:
for (var prefix = 624; prefix <= 626; prefix++) {
    var prefix = prefix.toString();
    for (var length = 16; length <= 19; length++) {
      var cardNumber = prefix + randomDigits.slice(0, length - prefix.length);
      it('as a prefix of ' + prefix + ' and a length of ' + length, function () {
        detectNetwork(cardNumber).should.equal('China UnionPay');
      });
    }
  }
Could anyone explain why this happen? Is this due to the it function?

*/

// https://www.builder.io/blog/visualizing-nodejs-close-queue

// NO ASYNC CODE -- everything NORMAL =)
for (var i = 0; i < 5; i++) {
  console.log(i);
}

// WE CANNOT USE SCOPE when working with ASYNC CODE
// event queue

// ASYNC CODE -- everything WEIRD!!
for (var i = 0; i < 5; i++) {
  // setTimeout === async function
  // setTimeout(function() {
  //   console.log(i);
  // }, 0)

  function wrapper (val) {
    setTimeout(function() {
      console.log(val);
    })
  }

  wrapper(i)
}

for (var i =0; i < 55; i++) {
  console.log('sync')
}

for (var i = 0; i < 2000; i++) {
  console.log('SYNC')
}

console.log('after all loops: ', i)