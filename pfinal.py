#!/usr/bin/python
# -*- coding: latin-1 -*-

#autores: Javier Diez Martinez  y  Alvaro Gonzalez Mejia grupo 42

import os, sys

#directorio trabajo

if(os.path.isdir("practicafinal")):
	os.system("rm -rf practicafinal")

os.system("mkdir practicafinal")
os.chdir("practicafinal")
os.system("wget http://idefix.dit.upm.es/download/cdps/p7/p7.tgz")
os.system("tar xfvz p7.tgz")
os.chdir("p7")
os.system("rm -rf p7.xml")
os.system("wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/p7.xml") 


#configuracion

os.system("./bin/prepare-p7-vm")
os.system("vnx -f p7.xml -v --destroy")
os.system("vnx -f p7.xml -v --create")

#configuracion de servidores de disco(nas)

os.system("lxc-attach -n nas1 -- gluster peer probe 10.1.3.21")
os.system("lxc-attach -n nas1 -- gluster peer probe 10.1.3.22")
os.system("lxc-attach -n nas1 -- gluster peer probe 10.1.3.23")
os.system("sleep 30")
os.system("lxc-attach -n nas1 -- gluster volume create nas replica 3 10.1.3.21:/nas 10.1.3.22:/nas 10.1.3.23:/nas force")
os.system("lxc-attach -n nas1 -- gluster volume start nas")
# puede haber error nas1,2,3 por direcciones ip

#configuracion servidores

os.system("lxc-attach -n s1 -- sudo mkdir /mnt/nas")
os.system("lxc-attach -n s1 -- sudo mount -t glusterfs 10.1.3.21:/nas /mnt/nas")
os.system("lxc-attach -n s2 -- sudo mkdir /mnt/nas")
os.system("lxc-attach -n s2 -- sudo mount -t glusterfs 10.1.3.21:/nas /mnt/nas")
os.system("lxc-attach -n s3 -- sudo mkdir /mnt/nas")
os.system("lxc-attach -n s3 -- sudo mount -t glusterfs 10.1.3.21:/nas /mnt/nas")
os.system("lxc-attach -n s4 -- sudo mkdir /mnt/nas")
os.system("lxc-attach -n s4 -- sudo mount -t glusterfs 10.1.3.21:/nas /mnt/nas")

#configuracion nagios

os.system("lxc-attach -n c3_nagios -- apt-get update")
os.system("lxc-attach -n c3_nagios -- apt-get install nano")
os.system("lxc-attach -n c3_nagios -- apt-get install apache2 -y")
os.system("lxc-attach -n c3_nagios -- apt-get install nagios3 -y")
os.system("lxc-attach -n c3_nagios -- service apache2 restart")

os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/s1_nagios2.cfg -P /etc/nagios3/conf.d")
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/s2_nagios2.cfg -P /etc/nagios3/conf.d")
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/s3_nagios2.cfg -P /etc/nagios3/conf.d")
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/s4_nagios2.cfg -P /etc/nagios3/conf.d")

os.system("lxc-attach -n c3_nagios -- rm -rf /etc/nagios3/conf.d/hostgroups_nagios2.cfg") 
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/hostgroups_nagios2.cfg -P /etc/nagios3/conf.d") 
os.system("lxc-attach -n c3_nagios -- service nagios3 restart") 
os.system("lxc-attach -n c3_nagios -- service apache2 restart") 

#configuracion server y tracks

os.system("rm -rf /etc/hosts")
os.system("wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/hosts/host/hosts -P /etc")

for n in range (1, 5):
	os.system("lxc-attach -n s"+str(n)+" -- apt-get update")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install software-properties-common -y")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install git -y")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install make g++ -y")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install python-software-properties -y")
	os.system("lxc-attach -n s"+str(n)+" -- add-apt-repository ppa:chris-lea/node.js -y")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get update")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install nodejs -y")


for n in range (2, 5):
	os.system("lxc-attach -n s"+str(n)+" -- git clone https://github.com/javier-diezmart/CDPSfyTracks")
	instru = "'cd /CDPSfyTracks/ && node app.js'"
	os.system('xterm -hold -e "lxc-attach -n s'+str(n)+' -- sh -c '+instru+'" &')
	#CDPSfyTracks es el nombre del APIREST

os.system("lxc-attach -n s1 -- rm -rf /etc/hosts")
os.system("lxc-attach -n s1 -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/hosts/s1/hosts -P /etc")

#os.system("lxc-attach -n s1 -- git clone https://github.com/javier-diezmart/CDPSfyMain")
#npm install en la MV
#os.system("lxc-attach -n s1 -- mkdir -p /data/db")
#os.system("lxc-attach -n s1 -- chmod +rwx /data/db")

#os.system("lxc-attach -n s1 -- mongodb > /dev/null 2>&1 &") arrancar la base de datos
#hayquehacer el npm start

#configuracion balanceador
os.system("xterm -hold -e 'lxc-attach -n lb -- xr --verbose --server tcp:0:80 --backend 10.1.2.14:5050 --backend 10.1.2.12:5050 --backend 10.1.2.13:5050 --web-interface 0:8001'")
