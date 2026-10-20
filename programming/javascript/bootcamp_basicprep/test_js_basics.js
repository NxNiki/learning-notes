console.log(Math.random());

// strings:
s = 'a'.repeat(10);
console.log(s);

obj = {'a': 1, 'b': 2};
string = JSON.stringify(obj);
console.log(string);

obj = {'b': 2, 'a': 1}
string = JSON.stringify(obj);
console.log(string);


function createSentence(words) {
    var sentence = "";
    for (var i = 0; i < words.length; i++) {
      // hint: does this line need to happen every iteration?
      
      if (i === words.length - 1) {
          sentence += '.';
      } else {
          sentence += words[i] + ' ';
      }
    }
  
    return sentence;
  }

// debug:
function keyOfObjectValue(object, target) {
    for (var key in object) {
      if (object[key] === target) {
        return key;
      } else {
        return -1;
      }
    }
  }


  // it seems var defined in for loop has scope only within the loop
arrayOfArrays = [[1,2,3], [4,5,6]];
function loopAnArrayOfArrays(arrayOfArrays) {
// create a loop which iterates over the input array
    // create an inner loop which iterates over current inner array
    // log current element to the console
    
    for (let i = 0; i < arrayOfArrays.length; i++) {
        array = arrayOfArrays[i];
        for (let i = 0; i < array.length; i++) {
            console.log(array[i]);
            console.log('inner: ' + i);
        }
        console.log('outer: ' + i);
    }
}

loopAnArrayOfArrays(arrayOfArrays)


function isItTruthy(param) {
    // if param is truthy
      // return 'Input is truthy'
    // otherwise
      // return 'Input is falsy'
      if (!param) {
          return 'Input is falsy';
      } else {
          return 'Input is truthy';
      }
  }


var result1 = isItTruthy('anything');
console.log('should log "Input is truthy":', result1);

var result2 = isItTruthy();
console.log('should log "Input is falsy":', result2);

var result3 = isItTruthy("");
console.log('should log "Input is falsy":', result3);

var result4 = isItTruthy(false);
console.log('should log "Input is falsy":', result4);


// check string in list:
array = ['flour', 'butter', 'sugar', 'eggs'];
target = 'sugar';
console.log(array.indexOf(target))

function findIngredient(ingredientList, ingredientToSearchFor) {
    // if ingredientToSearchFor is present within ingredientList
      // return '{ingredientToSearchFor} is on the list'
    // otherwise
      // return '{ingredientToSearchFor} is not on the list'
      
    // if (ingredientList.indexOf(ingredientToSearchFor) !== -1) {
    if (ingredientList.includes(ingredientToSearchFor)) {
        return `${ingredientToSearchFor} is on the list`;
    } else {
        return `${ingredientToSearchFor} is not on the list`;
    }
}

result = findIngredient(array, target);
console.log(result);






