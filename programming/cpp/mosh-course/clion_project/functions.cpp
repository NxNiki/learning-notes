// mosh course1: functions:

#include<iostream>
#include<limits>

using namespace std;

void greet(string firstName, string lastName) {
    cout << "Hello World" << endl;
    cout << "Hello " << firstName << " " << lastName << endl;
}

string fullName(string firstName, string lastName) {
    return firstName + " " + lastName;
}

void greet2(string name) {
    cout << "Hello " << name << endl;
}

int main() {
    greet("Xin", "Niu");
    cout << "Done" << endl;

    string name = fullName("Xin", "Niu");
    cout << name << endl;
    
    greet2(name);
    return 0;
}
