#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install qt5-default libqt5webkit5-dev build-essential python-lxml python-pip xvfb

pip install beautifulsoup4 requests dryscrape


#prepend the users home directory in python script
sed -i "s;^SLADER_DIR.*;SLADER_DIR\=\"$HOME/.slader/\";" slader.py

