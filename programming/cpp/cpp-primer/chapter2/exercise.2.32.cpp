#include<iostream>
int main ()
{
    int null = 0, *p = &null;
    // std::cout << p << ': ' << *p << std::endl;
    std::cout << reinterpret_cast<void*>(p) << ": " << *p << std::endl;
    return 0;
}
