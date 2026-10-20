var robotValueCounter = function(robot1, robot2, value) {

  var count = {value: 0};

  var recursion = function(robot) {
    // for each key in robot1:
    robot.forEach(function(val, key) {
      // add count if val === value:
      if (val === value) {
        count[value]++;
      } else if (typeof value === 'object' && !Array.isArray(value) ) {
        recursion(robot[key]);
      }
    });
  };

  recursion(robot1);
  recursion(robot2);

  return count;

};

var x13 = {
  name: 'x13',
  canFly: true,
  canCook: false,
  yearsInspected: [2002, 2005, 2010],
  fueledBy: "cookies",
  bestFriend: {
    name: "z09",
    yearsKnown: 4,
    isCharging: true
  }
};

var z09 = {
  name: 'z09',
  canFly: false,
  canCook: true,
  yearsInspected: [1998, 2005, 2018],
  fueledBy: "jealousy",
  bestFriend: {
    name: "r04",
    yearsKnown: 12,
    isCharging: false
  }
};

console.log(robotValueCounter(x13, z09, false));