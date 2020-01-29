#!/bin/sh
while read -r line; do export $line; done < ../.env && python3 ./server.py


