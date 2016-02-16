#CFLAGS = $(WARN) $(INC) $(LIB)
# List all your .cc files here (source files, excluding header files)
BINDIR = bin/
SRCDIR = src/
PYDIR = pyapi/
LIBDIR = lib/
JSONDIR = json/


#################################
# default rule
all:
	cd freedmqtt;git pull origin master; python setup.py install --force;
	@echo "***********COMPLETED COMPILATION**********"




