/*
Flip every chunk of n characters in a string, where n is any positive integer greater than 1.

Note that this is intentionally very similar to the previous problem.

Please focus on getting a working solution with the tools you know well.

Practice the interactive/collaborative interview style that's described in the documentation.

Example:
var input = 'a short example';
var output = flipEveryNChars(input, 5);
console.log(output); // --> ohs axe trelpma

Breaking this example down piece by piece:
'a sho' -> 'ohs a'
'rt ex' -> 'xe tr'
'ample' -> 'elpma'

-> 'ohs axe trelpma'
*/

// Submit de-obfuscated code

function flipEveryNChars(string, n) {
    if (string.length < 2) {
        return string;
    }

    let flipedString = '';
    for (let i = 0; i < string.length; i += n) {
        flipedString += string.slice(i, i+n).split('').reverse().join('');
    }
    return flipedString;
}


function assertEqual(actual, expected, testName) {
    if (actual === expected) {
        console.log('passed');
    } else {
        console.log(`FAILED [${testName}] expected: ${expected}, but got ${actual}`);
    }
}

var input = 'a short example';
var output = flipEveryNChars(input, 5);
var expected = 'ohs axe trelpma';
assertEqual(output, expected, 'should flip every 5 chars');
console.log(output); // --> ohs axe trelpma