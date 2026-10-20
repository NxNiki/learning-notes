function hello () {
  // default name is "world"
  name = name || 'world';
  // log
  console.log('Hello ' + name + '!');
}

hello();

