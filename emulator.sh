#!/bin/bash

#Run script for emulator distributed as part of 
#Number of parameters: 9
#Parameter:
#    $1:  <emulator's receiving UDP port number in the forward(sender) direction>
#    $2:  <receiver’s network address>
#    $3:  <receiver’s receiving UDP port number>
#    $4:  <emulator's receiving UDP port number in the backward(receiver) direction>
#    $5:  <sender’s network address>
#    $6:  <sender’s receiving UDP port number>
#    $7:  <maximum delay of the link in units of millisecond>
#    $8:  <packet discard probability>
#    $9:  <verbose-mode> (Boolean: Set to 1, the network emulator will output its internal processing).

# TESTING
./nEmulator-linux386 45509 "ubuntu1804-002" 62306 63068 "ubuntu1804-004" 7848 1 0.2 1
