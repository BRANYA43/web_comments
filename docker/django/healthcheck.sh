#!/bin/bash

curl --fail -s http://0.0.0.0:8000/api/docs || exit 1
