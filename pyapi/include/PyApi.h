#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <iostream>

#ifndef PYAPI
#define PYAPI

class PyApi
{
private:
	PyObject *rd;
	PyObject *wr;
	PyObject *dev;
	PyObject *sysPath;

public:
	PyApi(const char*);
	//int py_init(char*);
	int py_read(const char*,double*);
	int py_read(const char*,char*);
	int py_write(const char*,double);
	int py_write(const char*,char*);
	~PyApi();
};
#endif