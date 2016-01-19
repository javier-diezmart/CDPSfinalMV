#!/usr/bin/python
# -*- coding: latin-1 -*-

#Practica Final 2

#Autores: Javier Diez Martinez  y  Alvaro Gonzalez Mejia grupo 42
#Script de arranque del escenario de MV's con su correspondiente configuración

import os, sys

#DIRECTORIO DE TRABAJO

#Comprobamos si existe ya una carpeta con el mismo nombre y si asi, la borramos
if(os.path.isdir("practicafinal")):
	os.system("rm -rf practicafinal")

#Creamos de nuevo la carpeta y en ella descomprimimos el escenario virtual, importando nuestro p7.xml modificado
os.system("mkdir practicafinal")
os.chdir("practicafinal")
os.system("wget http://idefix.dit.upm.es/download/cdps/p7/p7.tgz")
os.system("tar xfvz p7.tgz")
os.chdir("p7")
os.system("rm -rf p7.xml")
os.system("wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/p7.xml") 


#ESCENARIO VIRTUAL

#Destruimos el escenario virtual y creamos uno nuevo
os.system("./bin/prepare-p7-vm")
os.system("vnx -f p7.xml -v --destroy")
os.system("vnx -f p7.xml -v --create")


#CONFIGURACION DE GLUSTERFS

#1-Configuracion de servidores de disco (nas)
os.system("lxc-attach -n nas1 -- gluster peer probe 10.1.3.21")
os.system("lxc-attach -n nas1 -- gluster peer probe 10.1.3.22")
os.system("lxc-attach -n nas1 -- gluster peer probe 10.1.3.23")
os.system("sleep 30")
os.system("lxc-attach -n nas1 -- gluster volume create nas replica 3 10.1.3.21:/nas 10.1.3.22:/nas 10.1.3.23:/nas force")
os.system("lxc-attach -n nas1 -- gluster volume start nas")

#2-Configuracion del montaje desde servidores web
os.system("lxc-attach -n s1 -- sudo mkdir /mnt/nas")
os.system("lxc-attach -n s1 -- sudo mount -t glusterfs 10.1.3.21:/nas /mnt/nas")
os.system("lxc-attach -n s2 -- sudo mkdir /mnt/nas")
os.system("lxc-attach -n s2 -- sudo mount -t glusterfs 10.1.3.21:/nas /mnt/nas")
os.system("lxc-attach -n s3 -- sudo mkdir /mnt/nas")
os.system("lxc-attach -n s3 -- sudo mount -t glusterfs 10.1.3.21:/nas /mnt/nas")
os.system("lxc-attach -n s4 -- sudo mkdir /mnt/nas")
os.system("lxc-attach -n s4 -- sudo mount -t glusterfs 10.1.3.21:/nas /mnt/nas")


#CONFIGURACION DE NAGIOS EN C3_NAGIOS

#Descargamos e instalamos paquetes necesarios para la monitorizacion
os.system("lxc-attach -n c3_nagios -- apt-get update")
os.system("lxc-attach -n c3_nagios -- apt-get install nano")
os.system("lxc-attach -n c3_nagios -- apt-get install apache2 -y")
os.system("lxc-attach -n c3_nagios -- apt-get install nagios3 -y")
os.system("lxc-attach -n c3_nagios -- service apache2 restart")

#Descargamos los ficheros de configuracion de nagios para S1, S2, S3 y S4
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/s1_nagios2.cfg -P /etc/nagios3/conf.d")
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/s2_nagios2.cfg -P /etc/nagios3/conf.d")
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/s3_nagios2.cfg -P /etc/nagios3/conf.d")
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/s4_nagios2.cfg -P /etc/nagios3/conf.d")

#Borramos y descargamos nuestro fichero ya modificado hostgroups_nagios2.cfg
#Relanzamos apache2 y nagios3
os.system("lxc-attach -n c3_nagios -- rm -rf /etc/nagios3/conf.d/hostgroups_nagios2.cfg") 
os.system("lxc-attach -n c3_nagios -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/nagios/hostgroups_nagios2.cfg -P /etc/nagios3/conf.d") 
os.system("lxc-attach -n c3_nagios -- service nagios3 restart") 
os.system("lxc-attach -n c3_nagios -- service apache2 restart")

### Opcion de no configuracion
#Contraseña: nagios
#Usuario: nagiosadmin


#CONFIGURACION DE S1, S2, S3 Y S4

#Borramos y descargamos el fichero /etc/hosts modificado para redirija a las direcciones www.server.cdpsfy.es y www.tracks.cdpsfy.es en Host
os.system("rm -rf /etc/hosts")
os.system("wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/hosts/host/hosts -P /etc")

#Descargamos e instalamos paquetes necesarios en S1, S2, S3 y S4
for n in range (1, 5):
	os.system("lxc-attach -n s"+str(n)+" -- apt-get update")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install software-properties-common -y")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install git -y")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install make g++ -y")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install python-software-properties -y")
	os.system("lxc-attach -n s"+str(n)+" -- add-apt-repository ppa:chris-lea/node.js -y")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get update")
	os.system("lxc-attach -n s"+str(n)+" -- apt-get install nodejs -y")

#Descargamos el proyecto CDPSfyTracks que va a correr en S2, S3 y S4. Lo ejecutamos
for n in range (2, 5):
	os.system("lxc-attach -n s"+str(n)+" -- git clone https://github.com/javier-diezmart/CDPSfyTracks")
	instru = "'cd /CDPSfyTracks/ && node app.js'"
	os.system('xterm -hold -e "lxc-attach -n s'+str(n)+' -- sh -c '+instru+'" &')
	#CDPSfyTracks es el nombre del APIREST

#Borramos y descargamos el fichero /etc/hosts modificado para redirija a las direcciones www.server.cdpsfy.es y www.tracks.cdpsfy.es en S1
os.system("lxc-attach -n s1 -- rm -rf /etc/hosts")
os.system("lxc-attach -n s1 -- wget https://raw.githubusercontent.com/javier-diezmart/CDPSfinalMV/master/hosts/s1/hosts -P /etc")

###En S1:
#git clone https://github.com/javier-diezmart/CDPSfyMain
#cd CDPSfyMain
#mkdir -p /data/db")
#chmod +rwx /data/db")
#npm install mongoose --save-dep
#npm install --save request
#mongod > /dev/null 2>&1 &
#npm start


#CONFIGURACION DEL BALANCEADOR DE CARGA

#Ponemos a correr el balanceador de carga CrossRoads. Escucha en el puerto 80 del LB, define tres servicios activos en S2, S3 y S4 y arranca un servidor web para su gestion en el puerto 8001 del LB
os.system("xterm -hold -e 'lxc-attach -n lb -- xr --verbose --server tcp:0:80 --backend 10.1.2.14:5050 --backend 10.1.2.12:5050 --backend 10.1.2.13:5050 --web-interface 0:8001'")
