FROM ubuntu:16.04

ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3.7 python3.7-dev python3-pip python3-setuptools python3-wheel gcc
RUN apt-get install -y git

RUN python3.7 -m pip install pip --upgrade

ADD . /simplog/simplog

EXPOSE 8080

ENV PYTHONPATH /simplog
WORKDIR /simplog/simplog

RUN pip3 install -r requirements.txt

CMD python3.7 -u apiserver.py
