#!/bin/bash
sudo apt-get install qt5-default libqt5webkit5-dev build-essential python-lxml python-pip xvfb

pip install beautifulsoup4 requests dryscrape

#prepend the users home directory in python script
sed -i "1s;^;SLADER_DIR=\"$HOME\"\n;" slader.py