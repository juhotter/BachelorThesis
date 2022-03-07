#!sbin/sh
#installieren:
#pip3 install frida-tools
#pip3 install objection
ADB=/usr/bin/adb
#DOTO1: ALLE APPS MÜSSEN IM SELBEN VERZEICHNIS WIE DAS SCRIPT LIEGEN
#DOTO2: ALLE APK NAMEN EINTRAGEN UND LOS GEHTS ( hint: apk muss so heißen wie die app selbst )








# vorher frida server
echo Checking Device Architekture..
adb shell getprop ro.product.cpu.abi
echo 32 bit.. # wenn nichts dabeisteht dann ist es 32 bit ( mein gerät ) 


#downloaded server aufs handy laden ( in frida-server umbennen)
adb push frida-server  /data/local/tmp/ 


echo Rechte werden vergeben
adb shell "chmod 777 /data/local/tmp/frida-server"



echo Frida Server hat folgende Rechte...
adb shell "su -c 'ls -all data/local/tmp | grep frida-server'"


echo Frida server wird nun gestartet 
#hier bleibt server gestartet -  neu .sh Datei für weiteres vorgehen
chmod u+r+x frida2.sh
#hier muss geändert werden falls ein anderen ausführt
osascript -e 'tell app "Terminal" to do script "/Users/julianhotter/desktop/thesis/script_frida2.sh"'  

adb shell "su -c './data/local/tmp/frida-server'"















