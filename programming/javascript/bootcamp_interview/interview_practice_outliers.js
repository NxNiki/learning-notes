/*
Given a string of even and odd numbers, find which is the sole even number or the sole odd number.

The return value should be 1-indexed, not 0-indexed.

Examples :
detectOutlierValue("2 4 7 8 10"); // => 3 - Third number is odd, while the rest of the numbers are even
detectOutlierValue("1 10 1 1");  //=> 2 - Second number is even, while the rest of the numbers are odd
*/


// Submit de-obfuscated code

function detectOutlierValue(string) {
    let array = string.split(' ')
    // return 0 if length of array is less than 3.
    if (array.length < 3) {
        return 0;
    }
    
    // transverse the array:
    // count the number of even numbers.
    let evenCount = 0;
    // get the index of first even and odd number.
    let firstEvenIndex = -1;
    let firstOddIndex = -1;
    for (let i = 0; i < array.length; i++) {
        if (Number(array[i]) % 2 === 0) {
            if (firstEvenIndex === -1) {
                firstEvenIndex = i;
            }
            evenCount += 1;
        } else if (firstOddIndex === -1) {
            firstOddIndex = i;
        }
    }
    
    // return the index of first even number if number of even numbers is equal to 1.
    // otherwise return the index of first odd number.
    if (evenCount === 1) {
        return firstEvenIndex + 1;
    } else {
        return firstOddIndex + 1;
    }
    
}

function assertEqual(actual, expected, testName) {
    if (actual === expected) {
        console.log('passed');
    } else {
        console.log(`FAILED [${testName}] expected: ${expected}, but got: ${actual}`);
    }
}

output1 = detectOutlierValue("2 4 7 8 10"); // => 3 - Third number is odd, while the rest of the numbers are even
expect1 = 3;
assertEqual(output1, expect1, 'should return position of first odd number')

output2 = detectOutlierValue("1 10 1 1");  //=> 2 - Second number is even, while the rest of the numbers are odd
expect2 = 2
assertEqual(output2, expect2, 'should return position of first even number')
