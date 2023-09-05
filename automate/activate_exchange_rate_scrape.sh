#!/bin/bash
docker run --rm -v $(pwd):/home/db python-scrape-env python /home/db/automate/exchange_rate.py