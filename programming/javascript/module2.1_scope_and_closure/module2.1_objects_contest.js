var a_variable = { a : 1 };
a_variable.a_property = { b : 2 };

console.log(a_variable);

// { c : 3 }.a_property = { b : 2 }; // this won't work, the brace is interpreted as the opening of a block.

console.log(({ c : 3 }).a_property = { b : 2 });
