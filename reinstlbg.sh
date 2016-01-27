cd /usr/local/lbneo/virtenvlb3.2/src/LBGenerator
/usr/local/lbneo/virtenvlb3.2/bin/python3.2 setup.py install
chown -R apache /usr/local/lbneo/*
chown -R :apache /usr/local/lbneo/*
chmod -R 755 /usr/local/lbneo/*
chown -R apache /var/www/*
chown -R :apache /var/www/*
chmod -R 755 /var/www/*
# rm -f /usr/local/lbneo/virtenvlb3.2/src/LBGenerator/pp_f_log.log
service httpd restart

