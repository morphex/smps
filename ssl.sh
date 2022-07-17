#!/bin/bash

# Script to setup ssl certificate and key

mkdir -p ssl
openssl req -newkey rsa:4096 -x509 -sha256 -days 3650 -nodes -out ./ssl/cert.pem -keyout ./ssl/key.pem
