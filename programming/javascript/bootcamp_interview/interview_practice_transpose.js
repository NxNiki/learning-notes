/*
You will be given an array that contains two strings. Your job is to create a function that will take those two strings 
and transpose them, so that the strings go from top to bottom instead of left to right.

e.g. transposeTwoStrings(['Hello','World']);

should return:
H W  
e o  
l r  
l l  
o dx
*/

function transposeTwoStrings(arrayOfTwoStrings) {
    let string1 = arrayOfTwoStrings[0];
    let string2 = arrayOfTwoStrings[1];
    let maxStringLength = Math.max(string1.length, string2.length);
    let transposedStrings = "";
    
    for (let i = 0; i < maxStringLength; i++) {
        if (i < string1.length) {
            transposedStrings += string1[i];
        } else {
            transposedStrings += " ";
        }
        transposedStrings += " ";
        if (i < string2.length) {
            transposedStrings += string2[i];
        }
        transposedStrings += "\n";
    }
    return transposedStrings;
}

console.log(transposeTwoStrings(['Hello','World']))
console.log(transposeTwoStrings(['Hello','World!']))
console.log(transposeTwoStrings(['Hello!','World']))

