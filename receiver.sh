#!/bin/bash

#Run script for receiver distributed as part of 
#Assignment 2
#Computer Networks (CS 456/656)
#Number of parameters: 4
#Parameter:
#    $1:  <hostname of the network emulator>
#    $2:  <UDP port number used by the link emulator to receive ACKs from the receiver>
#    $3:  <UDP port number used by the receiver to receive data from the emulator>
#    $4:  <name of the file into which the received data is written>

#For Python implementation
# python3 receiver.py $1 $2 $3 "$4"

# testing for now
python3 receiver.py "ubuntu1804-008" 63068 62306 "output.txt"

