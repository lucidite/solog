FROM python:3.7-slim

ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc

EXPOSE 8080

COPY . /simplog/simplog
ENV PYTHONPATH /simplog
WORKDIR /simplog/simplog

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python", "-u", "apiserver.py"]
