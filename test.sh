#!/bin/bash

if [[ ! -f ./ssl/cert.pem ]]; then
    echo "Setting up SSL first"
    ./ssl.sh
fi

echo "Start time `date`"
./smps.py &>smps.log&
smps_pid=$!
echo SMPS running at pid $smps_pid
sleep 2
./client.py $1

echo "Test complete"
echo "End time `date`"
