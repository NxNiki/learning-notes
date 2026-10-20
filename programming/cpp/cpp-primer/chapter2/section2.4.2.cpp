#include<iostream>

int main ()
{
    const double pi = 3.14;
    // double *ptr = &pi;
    const double *cptr = &pi;
    // *cptr = 42;

    double dval = 3.14;
    cptr = &dval;
    std::cout << *cptr << std::endl;

    // double &r1 = pi;
}
