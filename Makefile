#

prefix = /usr/local
bindir = $(prefix)/bin

all:

install: all
	test -d $(bindir) || mkdir -vp $(bindir)
	install -m 755 -T gitsh.py $(bindir)/gitsh
