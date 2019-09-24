#!/bin/bash

#Run script for sender distributed as part of 
#Assignment 2
#Computer Networks (CS 456/656)
#Number of parameters: 4
#Parameter:
#    $1:  <hostname of the network emulator>
#    $2:  <UDP port number used by the emulator to receive data from the sender>
#    $3:  <UDP port number used by the sender to receive ACKs from the emulator>
#    $4:  <name of the file to be transferred>

#For Python implementation
# python3 sender.py $1 $2 $3 "$4"

# TESTING
python3 sender.py "ubuntu1804-008" 45509 7848 "input.txt"
