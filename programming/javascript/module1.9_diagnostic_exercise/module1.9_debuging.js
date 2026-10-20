var currentInventory = {
  shoes: [
    {name: 'tasselled black low-top lace-up', price: 1000, designer: 'Brunello Cucinelli'},
    {name: 'tasselled green low-top lace-up', price: 1100, designer: 'Gucci'},
    {name: 'plain beige suede moccasin', price: 950, designer: 'Balenciaga'},
    {name: 'plain olive suede moccasin', price: 2000, designer: 'Balenciaga'}
  ]
};

var getAveragePriceForShoes = function(inventory){
    var avgShoePrice;
    var totalShoeCount = 0;
    var totalShoeCost = 0;

    var shoeList = inventory['shoes'];
    for (var i = 0; i < shoeList.length; i++) {
        var currentShoe = shoeList[i];

        totalShoeCost += currentShoe['price'];
        totalShoeCount++;
    }
    console.log(totalShoeCost, totalShoeCount);
    avgShoePrice = totalShoeCost/totalShoeCount;
    return avgShoePrice;
};

getAveragePriceForShoes(currentInventory); // NaN
