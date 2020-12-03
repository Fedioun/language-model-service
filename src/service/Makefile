
all:
EXTRA_CXXFLAGS = -Wno-sign-compare
include ../config.mk

BINFILES = decode-faster-service decode-faster-two-pass decode-faster-two-pass-service

OBJFILES =

ADDLIBS = ../lm/lm.a ../decoder/decoder.a ../lat/lat.a \
	  ../cpucompute/cpucompute.a  ../util/util.a ../base/base.a


TESTFILES =

include ../makefiles/default_rules.mk
