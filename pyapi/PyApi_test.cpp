#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <iostream>
#include <PyApi.h>


int main(int argc, char const *argv[])
{
	PyApi dev1("TEST_1");
	char name[128];
	char* test_str  = "HELLO";
	//dev1.py_init("dev1.json");
	dev1.py_read("Vendor_name", name);
	if(strcmp(name,"FREEDM"))
	{
		std::cout<<"TEST FAILED"<<std::endl;
		std::cout<<"READ: "<<name<<std::endl;
		return 1;
	}
	else
		std::cout<<"TEST PASSED"<<std::endl;
	dev1.py_write("Vendor_name",test_str);
	dev1.py_read("Vendor_name", name);
	if(strcmp(name,test_str))
	{
		std::cout<<"TEST FAILED"<<std::endl;
		std::cout<<"READ: "<<name<<std::endl;
		return 1;
	}
	else
		std::cout<<"TEST PASSED"<<std::endl;
		return 0;
}