// Function name as a string
const functionName = 'sort';

// Sample array
const myArray = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5];

// Check if the function exists in the current scope
if (typeof window[functionName] === 'function') {
  // Apply the function to the array using .apply()
  const result = window[functionName].apply(null, [myArray.slice()]); // Use slice to create a copy of the array
  console.log(result);
} else {
  console.error(`${functionName} is not a valid function.`);
}
