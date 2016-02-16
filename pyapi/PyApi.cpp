#include <Python.h>
#include <stdio.h>
#include <string.h>
#include <iostream>
#include "PyApi.h"


PyApi::PyApi(const char* file)
{
	Py_Initialize();
    const char* app = "C_Application";
    sysPath = PySys_GetObject((char*)"path");
    PyObject* curDir = PyString_FromString(".");
    PyList_Append(sysPath, curDir);
    Py_DECREF(curDir);
    PyObject* dev_prof = PyImport_ImportModule("freedmqtt.DeviceProfile");
    if (!dev_prof)
    {
        PyErr_Print();
        //return 0;
    }
    dev = PyObject_GetAttrString(dev_prof,"DeviceProfile");
    Py_DECREF(dev_prof);
    if (!dev)
    {
        PyErr_Print();
        //return 0;
    }
    PyObject* args = Py_BuildValue("(ss)",file,app);
    dev = PyObject_CallObject(dev,args);
    if (!dev)
    {
        PyErr_Print();
        //return 0;
    }
    rd = PyObject_GetAttrString(dev, "read");
    wr = PyObject_GetAttrString(dev, "write");
    if (!rd || !wr)
    {
        PyErr_Print();
        //return 0;
    }  
    Py_DECREF(args);
    //return 1;
}

// int PyApi::py_read(char* attribute,int index, double* result)
// {
//     PyObject* args = Py_BuildValue("(si)",attribute,index);
//     if (!args)
//     {
//         PyErr_Print();
//         return 0;
//     } 
//     PyObject* resultObject = PyObject_CallObject(rd,args);
//     if (!resultObject)
//     {
//         PyErr_Print();
//         return 0;
//     }
//     *(result) = PyFloat_AsDouble(resultObject);
//     Py_DECREF(args);
//     Py_DECREF(resultObject);
//     return 1;
// }

int PyApi::py_read(const char* attribute,double* result)
{
    PyObject* args = Py_BuildValue("(s)",attribute);
    if (!args)
    {
        PyErr_Print();
        return 0;
    } 
    PyObject* resultObject = PyObject_CallObject(rd,args);
    if (!resultObject)
    {
        PyErr_Print();
        return 0;
    }
    *(result) = PyFloat_AsDouble(resultObject);
    Py_DECREF(args);
    Py_DECREF(resultObject);
    return 1;
}

int PyApi::py_read(const char* attribute, char* result)
{
    PyObject* args = Py_BuildValue("(s)",attribute);
    if (!args)
    {
        PyErr_Print();
        return 0;
    } 
    PyObject* resultObject = PyObject_CallObject(rd,args);
    if (!resultObject)
    {
        PyErr_Print();
        return 0;
    }
    char* tempresult = PyString_AsString(resultObject);
    //result = (char*) malloc(sizeof(char) * strlen(tempresult));
    strcpy(result,tempresult);
    Py_DECREF(args);
    Py_DECREF(resultObject);
    return 1;
}

// int PyApi::py_write(char* attribute,int index, double* value)
// {
//     PyObject* args = Py_BuildValue("(fsi)",value,attribute,index);
//     if (!args)
//     {
//         PyErr_Print();
//         return 0;
//     } 
//     PyObject* resultObject = PyObject_CallObject(wr,args);
//     if (!resultObject)
//     {
//         PyErr_Print();
//         return 0;
//     }
//     Py_DECREF(args);
//     Py_DECREF(resultObject);
//     return 1;
// }

int PyApi::py_write(const char* attribute,double value)
{
    PyObject* args = Py_BuildValue("(fs)",value,attribute);
    if (!args)
    {
        PyErr_Print();
        return 0;
    } 
    PyObject* resultObject = PyObject_CallObject(wr,args);
    if (!resultObject)
    {
        PyErr_Print();
        return 0;
    }
    Py_DECREF(args);
    Py_DECREF(resultObject);
    return 1;
}

int PyApi::py_write(const char* attribute, char* value)
{
    PyObject* args = Py_BuildValue("(ss)",value,attribute);
    if (!args)
    {
        PyErr_Print();
        return 0;
    } 
    PyObject* resultObject = PyObject_CallObject(wr,args);
    if (!resultObject)
    {
        PyErr_Print();
        return 0;
    }
    Py_DECREF(args);
    Py_DECREF(resultObject);
    return 1;
}

PyApi::~PyApi()
{
    Py_DECREF(rd);
    Py_DECREF(wr);
    Py_DECREF(dev);
    Py_DECREF(sysPath);
    Py_Finalize();
    //return 0;
}