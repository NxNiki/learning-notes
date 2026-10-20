// patients is the first skill of a good programmer.

#include <iostream>
#include <limits>

int variables() {
//    int file_size;
//    file_size = 100;
//    int file_size = 100, counter = 0;
    // it is best practice to declare variables in separate lines:
    int file_size = 100;
    int counter = 0;
    double sales = 9.00;

    std::cout << file_size << std::endl;
    return 0;
}

using namespace std;
int swap_variable() {
    int a = 1;
    int b = 2;

    int temp = a;
    a = b;
    b = temp;

    cout << a << std::endl;
    cout << b << std::endl;
    return 0;
}

// constant: avoid values from being changed.
void const_variable() {
    const double pi = 3.14;
}

void mathematical_expression() {
    // int x = 10;
    double x = 10; // to make floating point number of z, set x as double type.
    int y = 3;
    double z = x / y;
    cout << z << endl;
}

void mathematical_expression2() {
    int x = 10;
    // int y = x++; // y = 10, x = 11
    int y = x--; // y = 9, x = 9
    --x;
    ++x;
    int z = x % y;
}
void order_of_operations() {
    // order of operations:
    int x = 1 + 2 * 3;
    int y = 10;
    double x2 = (1 + 2) * 3;
    double z = (x + 10) / (3 * y);

    cout << z << endl;
}

void writing_to_console() {
    int x = 10;
    std::cout << "x = ";
    std::cout << x << endl;
    std::cout << "x =" << x << endl;
}

int read_from_console() {
    cout << "Enter a value:"; // << string insertion operator
    int value;
    cin >> value; // >> string extraction operator
    cout << value;

    cout << "Enter x and y:";
    int x;
    int y;
//    cin >> x;
//    cin >> y;
    cin >> x >> y;
    cout << x + y;
    return 0;
}

#include <cmath>

int cmath_library() {
    double result = floor(1.2);
    cout << result;
    return 0;
}

// Fundamental Data Types:
// C++ is a statically-typed language

int data_types() {
    double price = 0.99;
    float interestRate = 3.67F;
    // adding F/f to float variable or compiler will store double number into a float variable. and will cause data lose.
    long fileSize = 90000l;
    // add L/l to long format number.
    char letter = 'a';
    bool isValid = true;

    // auto keyword is useful when working with complex data types
    auto price2 = 0.99;
    auto interestRate2 = 3.67F;
    auto fileSize2 = 90000l;
    auto letter2 = 'a';
    auto isValid2 = true;

    // brace initialization:
    int number = 1.2;
//    int number2 {1.2}; // it will raise error if the data type doesn't match
    int number3 {}; // initialize number3 as 0 if no value is provided.
}

void working_with_numbers() {
    int number_bin = 0b11111111; //binary number
    int number_hex = 0xFF;
    cout << number_hex;

    unsigned int number_us = 0;
    number_us --;
    cout << number_us; // this will result in a large number, be careful when using unsigned numbers.
}

void narrowing() {
    int number = 1'000'000;
    short another = number; // narrowing int to short
//    short another_brace {number}; //this will raise an error.

    short number2 = 100;
    int another2 = number; // assign smaller number to a larger memory space is not an issue. additional bytes in memory will be filled with 0.
    short another_brace2 {number2}; // this will not raise an error.
}

# include <cstdlib>
# include <ctime>

void random_number() {
    long elapsedSeconds = time(nullptr); // # of seconds from Jan 1 1970. or time(0).
    srand(elapsedSeconds);
    int number = rand() % 10; // number from 0 to 9.
    int dice = rand() % (6 - 1 + 1) + 1; // rand() % (maxValue - minValue + 1) + minValue;
    cout << number;
}

# include <iomanip>

void format_output() {
//    cout << left << setw(10) << "Spring" << setw(10) << "Nice" << endl
//         << setw(10) << "Summer" << setw(10) << "Hot";

    cout << left; // right alignment is default, so don't need to set right.
    // the above is a sticky manipulator, once it is applied it is going to be in effect until we change it.
    cout << setw(10) << "Spring" << setw(10) << "Nice" << endl
    // setw() is not sticky, so it only applies to what comes after.
         << setw(10) << "Summer" << setw(10) << "Hot" << endl;

    cout << fixed << setprecision(10) << 12.34567 << endl
         << 22.345677;
}

void data_type_size() {
    cout << sizeof(int) << endl; // number of bytes used to store an integer.
    cout << std::numeric_limits<int>::min() << endl
         << numeric_limits<int>::max() << endl;

    // if number exceeds the range of max value of the data type, it will wrap around to the type's minimum
    // which is called overflowing.
    int number = numeric_limits<int>::max();
    number++;
    cout << number << endl;

    // underflow:
    int min_number = numeric_limits<int>::min();
    min_number--;
    cout << min_number << endl;
}

void booleans() {
    bool isNew = false;
    cout << isNew << endl;
    cout << boolalpha << isNew << endl;
    // boolalpha is a sticky manipulator, so once applied it will be in effect until we turn it off.
    cout << noboolalpha << isNew << endl;
}

void char_string() {
    char ch = 'a';
    cout << ch << endl;
    cout << +ch << endl; // + tells compiler to treat ch as a number.

    char ch2 = 98; // not a good way to write code.
    cout << ch2 << endl;
    cout << +ch2 << endl;

//    string name = "Mosh Hamedani";
    string name;
    cout << "Enter your name: ";
//    cin >> name; // this does not read string after space.
    std::getline(cin, name);
    cout << "Hi " << name;
}

void arrays() {
    int numbers[5];
    cout << numbers << endl;
    cout << numbers[0] << endl;
    cout << numbers[5] << endl; // C++ do not prevent accessing elements outside of array.

    int numbers2[5] = {0, 1, 2};
    int numbers3[] = {2, 4, 9};

    string names[3];
    cout << "Name: " << endl;
    getline(cin, names[0]);

    cout << "Name: " << endl;
    getline(cin, names[1]);

    cout << "Name: " << endl;
    getline(cin, names[2]);
}

void type_conversion() {
    int x = 1;
    double y = 2.2;
    double z = x + y;
    cout << z << endl;

    int m = x + y; // conversion from double to int may lead to data lose.
    cout << m << endl;

    // use casting to explicitly tell the compiler that we want to convert data from one type to another:

    int n = x + (int)y; // C style casting.
    // Problem: if conversion cannot be done, we will not know until we run the compiled program
    cout << n << endl;

    int l = x + static_cast<int>(y); // C++ casting.
    // With C++ casting, we can catch conversion error at compile time. We don't have to run and test every feature to
    // see some conversion can be done or not.
    cout << l << endl;
}

void type_conversion2() {
    int x = 10;
    int y = 3;
    double z = x/y;
    cout << z << endl;
    double z2 = (double)x/y;
    cout << z2 << endl;
    double z3 = static_cast<double>(x) / y;
    cout << z3 << endl;
}

void comparison_operators() {
    int x = 10;
    int y = 3;
    bool result = x == y;
    cout << boolalpha << result;

    double z = 5;
    bool result2 = x==z;
    cout << result2;

    double m = 10;
    bool result3 = x == m;
    cout << result3;

    char first = 'a';
    char second = 'A';
    bool result4 = first == second;
    cout << result4 << endl;
}

void logical_operators() {
    int age = 30;
    bool isEligible = age > 18 && age < 65;
    cout << isEligible << endl;
}

void order_of_logical_operators() {
    // ()
    // !
    // &&
    // ||

    bool a = true;
    bool b = true;
    bool c = false;

    //bool result = b && !a;
//    bool result = a || b && c;
    bool result = (a || b) && c;

    cout << boolalpha << result << endl;

}

void if_statements() {
    int temperature = 70;
    if (temperature < 60)
        cout << 'cold' << endl;
    else if (temperature < 90)
        cout << 'Nice' << endl;
    else
        cout << 'Hot' << endl;

    cout << 'done' << endl;

    // multiple expressions in if statement:
    if (temperature < 50) {
        cout << 'Cold' << endl;
        cout << 'Wear warm clothes' << endl;
    }

    // conditional operator:
    int sales = 11'000;
    double commission = (sales > 10'000) ? .1 : .05;
    cout << commission << endl;
}

void switch_statement() {
    cout << "1- Create Account" << endl
         << "2- Change password" << endl
         << "3- Quit" << endl
         << "Select an option: ";

    short input;
    cin >> input;

    switch (input) {
        case 1:
            cout << "You selected 1" << endl;
            break;
        case 2:
            cout << "You selected 2" << endl;
            break;
        default:
            cout << "Goodbye!" << endl;
    }
}

int main() {
    // cout is a feature in iostream short for 'character out'
    std::cout << "Hello, World!" << std::endl; // whenever type a statement, end with a semicolon.
//    variables();
//    swap_variable();
//    mathematical_expression();
//    writing_to_console();
//    read_from_console();
//    cmath_library();
//    string str = "abcdefg";
//    cout << str.substr(1);
//    format_output();
//    data_type_size();
//    booleans();
//    char_string();
//    arrays();
//    type_conversion();
//    type_conversion2();
    comparison_operators();
    logical_operators();
    order_of_logical_operators();
    if_statements();
    switch_statement();
    return 0; // 0 tells operating system that the program terminates correctly.
}















