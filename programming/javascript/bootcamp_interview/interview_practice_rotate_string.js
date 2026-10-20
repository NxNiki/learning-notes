/*
Is one string a rotated version of another?

For example:
String 1: 'hello world'
String 2: 'orldhello w'

Extra hint: (click the drop down to ROT7 to see hint)
If you double the string, you'll be able to find another string inside the doubled string using familiar String methods.

Doubled string: 'hello worldhello world'
Search w/in it: '       orldhello w    '
*/

function isRotated(string1, string2) {
    if (string1.length !== string2.length) {
        return false;
    }

    let string11 = string1 + string1;
    // for (let i = 0; i < string1.length; i++) {
    //     if (string11.slice(i, i + string1.length) === string2) {
    //         return true;
    //     }
    // }
    // return false;
    return string11.indexOf(string2) !== -1;
}

console.log(isRotated('hello world', 'orldhello w'))
console.log(isRotated('hello world', 'rldhello wo'))
console.log(isRotated('hello world', 'roldhello w'))
console.log(isRotated('helloworld', 'orldhello w'))