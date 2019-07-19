FROM ubuntu:18.04

RUN apt-get -y -m update && \
    apt-get install -y git cmake g++ gfortran python python-numpy python-pip python-six

# This ADD block forces a build (invalidates the cache) if the git repo contents have changed, otherwise leaves it untouched.
ADD https://api.github.com/repos/usnistgov/REFPROP-cmake/git/refs/heads/master RPcmake-version.json
RUN cd /root && \
    git clone --recursive https://github.com/usnistgov/REFPROP-cmake && \
    cd REFPROP-cmake/

WORKDIR /root/REFPROP-cmake/
CMD mkdir -p build &&\
    cd build && \
    cmake .. -DREFPROP_FORTRAN_PATH=/root/REFPROP-cmake/fortran/ && \
    cmake --build .