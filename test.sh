#!/bin/bash

if [[ ! -f ./ssl/cert.pem ]]; then
    echo "Setting up SSL first"
    ./ssl.sh
fi

./smps.py &
smps_pid=$!
echo SMPS running at pid $smps_pid
sleep 5
./client.py

echo "Test complete"
