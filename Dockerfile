FROM ubuntu:18.04

RUN apt-get -y -m update && \
    apt-get install -y git python3 python3-pip gcc-7 g++-7 gfortran-7 && \
    pip3 install CoolProp flask flask-restful werkzeug==2.0.3 && \
    mkdir -p /root/propAPIne
#uncomment next line if you want to use the Git version
#RUN cd /root && git clone https://github.com/mirokymac/propAPIne
COPY server /root/propAPIne/server
WORKDIR /root/propAPIne/server
EXPOSE 22001
CMD python3 app.py
