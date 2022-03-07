#frida-ps -U oder frida-ps -U -a um alle aufzulisten ; für normales frida: frida -U  -f zb. com.android.chrome
#adb push frida-script.js  /data/local/tmp/ 

#mention : im gegensatz zu anderen scripten wird hier jede app sequentiell anstatt parallel abgearbeitet



#DOTO APPS ANGEBENB
declare -a arr=( "slither.apk" "lulu.apk" )


cd /Users/julianhotter/desktop/thesis



echo Frida Server läuft auf:
frida-ps -U | grep frida-server 


echo Alle Apps werden installiert
for i in "${arr[@]}"
do
   adb install $i
done


# .apk abschneiden
declare -a onlynames=()
for i in "${arr[@]}"
do
    TEMP=$( echo $i | cut -d "." -f 1)
    onlynames+=($TEMP)
done


#package finden und dieses auch wieder schneiden
declare -a packagenames=()
declare -a uninstallnames=()
for i in "${onlynames[@]}"
do
    PACKAGENAME_TEMP=$(adb shell cmd package list packages | grep  $i )
    UNINSTALLNAME_TEMP=$( echo $PACKAGENAME_TEMP | cut -d ":" -f 2) 
    packagenames+=($PACKAGENAME_TEMP)
    uninstallnames+=($UNINSTALLNAME_TEMP)
done





echo App wird nun mit certifikate pinning disabled neu gestartet


# chmod u+r+x frida3.sh
  # osascript -e 'tell app "Terminal" to do script "/Users/julianhotter/desktop/thesis/frida3.sh"'  


for i in "${uninstallnames[@]}"
do
   
   echo neue app wird 20 sec lang aufgemacht
   frida --no-pause -U -l frida-script.js -f  $i &

#passiert nie
sleep 25 
adb uninstall  $i 



done



echo Server wieder herunterfahren..
PID=$(frida-ps -U | grep frida-server  | cut -d " " -f 2 )
adb shell "su -c 'kill $PID'"











