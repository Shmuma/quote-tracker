#!/bin/sh

socat -d TCP4-LISTEN:3128,fork,reuseaddr EXEC:./test.py