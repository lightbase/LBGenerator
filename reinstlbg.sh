cd /usr/local/lbneo/virtenvlb3.2/src/LBGenerator
/usr/local/lbneo/virtenvlb3.2/bin/python3.2 setup.py install
chown -R apache /usr/local/lbneo/virtenvlb3.2/*
chown -R :apache /usr/local/lbneo/virtenvlb3.2/*
chmod -R 700 /usr/local/lbneo/virtenvlb3.2/*
rm -f /usr/local/lbneo/virtenvlb3.2/src/LBGenerator/pp_f_log.log
service httpd restart

