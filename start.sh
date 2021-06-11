#! /bin/bash
source venv/bin/activate
git pull
pip3 install -r requirements.txt
python3 main.py