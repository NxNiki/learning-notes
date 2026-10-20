/*
Given a list of non-negative integers and a target sum, find a pair of numbers that sums to the target sum.

Example:

var pair = findPairForSum([3, 34, 4, 12, 5, 2], 9);
console.log(pair); // --> [4, 5]
*/

function findPairForSum(array, target) {
    let visited = new Set([]);
    for (let i = 0; i < array.length; i++) {
        if (visited.has(target - array[i])) {
            return [target - array[i], array[i]];
        } else {
            visited.add(array[i]);
        }
    }
}

function assertArrayEqual(actual, expected, testName) {
    let isEqual = true; 
    if (actual.length !== expected.length) {
        isEqual = false;
    }
    for (let i = 0; i < actual.length; i++) {
        if (actual[i] !== expected[i]) {
            isEqual = false;
            break;
        }
    }
    if (isEqual) {
        console.log('passed');
    } else {
        console.log(`FAILED [${testName} expected: ${expected}, but got ${actual}`);
    }
}

var pair = findPairForSum([3, 34, 4, 12, 5, 2], 9);
console.log(pair); // --> [4, 5]
assertArrayEqual(pair, [4, 5], 'should find pair sum to 9');