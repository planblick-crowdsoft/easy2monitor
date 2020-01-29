#!/bin/sh
(export $(cat .env | xargs) && python3 ./src/server.py)