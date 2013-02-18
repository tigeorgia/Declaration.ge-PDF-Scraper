#!/bin/bash

scripts/download reports 0 1000
scripts/download reports 43000 1000
scripts/tohtml reports/ka reports/ka
python file_output.py reports/ka
