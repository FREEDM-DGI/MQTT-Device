CC = g++
AR = ar
ARFLAG = -cvq
WARN = -Wall

PYDIR = /usr/include/
PYAPIDIR = ./
LIBDIR = /usr/lib/
LOGDIR = ../log/
INCDIR = /usr/include/
SRCDIR = ../src/
PROFDIR = ../conf/profile/

INC = -I./include/ -I$(PYDIR)python2.7
LD = -lpython2.7
PYSRC = $(PYAPIDIR)PyApi.cpp
PYLIB = libpyapi.a


all: pyapi
	cp ./include/*.h $(INCDIR)
	cp PyApi_test.cpp $(SRCDIR)
	cp TEST_1.xlsx $(PROFDIR)
	@echo "work done here..."

pyapi: $(PYSRC)
	$(CC) -c $(WARN) $(INC) $(PYSRC) $(LD)
	$(AR) $(ARFLAG) $(LIBDIR)$(PYLIB) *.o
	@echo "pyapi built"

clean:
	rm -f *.o $(LIBDIR)$(PYLIB)