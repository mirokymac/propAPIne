FROM ubuntu:18.04

RUN apt-get -y -m update && \
    apt-get install -y git python3 python3-pip gcc-7 g++-7 gfortran-7 && \
    pip3 install -y CoolProp flask flask-restful
RUN cd /root && \
    git clone https://github.com/mirokymac/propAPIne
WORKDIR /root/propAPIne/server
EXPOSE 22001
CMD python3 app.py
