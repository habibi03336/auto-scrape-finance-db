#!/bin/bash
docker run --rm -v $(pwd):/home/db python-scrape-env python /home/db/automate/scrape_finance.py