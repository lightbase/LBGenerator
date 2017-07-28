#!/bin/bash

rm -rf /var/log/lbg.log
cd "/usr/local/lb/ve32/src/liblightbase"
/usr/local/lb/ve32/bin/python3.2 setup.py install
cd "/usr/local/lb/ve32/src/LBGenerator"
/usr/local/lb/ve32/bin/python3.2 setup.py install
service nginx stop
service uwsgi stop
sleep 5
service uwsgi start
service nginx start
less +F /var/log/lbg.log
