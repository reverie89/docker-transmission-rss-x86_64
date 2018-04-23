#!/bin/bash

if [ ! -f /config/providers.txt ]; then
	cp /providers.txt /config/
fi

python /app.py
