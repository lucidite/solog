#!/bin/bash

# At first, create and activate proper virtualenv.
# (Not included here.)

# Install required packages.
pip3 install -r requirements.txt

# host address(-s):       localhost
# port number(-p):        8080
# log group name(-g):     samples
# key(-k), value(-v):     {"type": "sample"}
# number of logs(-n):     10
# sample data length(-d): 100
python3 client.py -s localhost -p 8080 -g samples -k type -v ss -n 10 -d 100
