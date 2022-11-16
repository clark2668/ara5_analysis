LDFLAGS=-L${ARA_UTIL_INSTALL_DIR}/lib -L${ARA_DEPS_INSTALL_DIR}/lib -L/${NUPHASE_INSTALL_DIR}/lib -L${shell root-config\
 --libdir}
CXXFLAGS=-I${ARA_UTIL_INSTALL_DIR}/include -I${ARA_DEPS_INSTALL_DIR}/include -I${NUPHASE_INSTALL_DIR}/include -I${shell\
 root-config --incdir}
CXXFLAGS += -std=c++11
LDLIBS += $(shell $(ROOTSYS)/bin/root-config --libs) -lAraEvent -lRootFftwWrapper

.PHONY: all

%: %.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(LDLIBS) -o $(@) $<

