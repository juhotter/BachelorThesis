#!sbin/sh
#zurNOT https://www.sisik.eu/apk-tool
ADB=/usr/bin/adb
#DOTO1: ALLE APPS MÜSSEN IM SELBEN VERZEICHNIS WIE DAS SCRIPT LIEGEN
#DOTO2: ALLE APK NAMEN EINTRAGEN UND LOS GEHTS ( hint: apk muss so heißen wie die app selbst )
declare -a arr=( "slither.apk" "lulu.apk")






echo Checking Devices...
adb devices

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


echo Alle Apps werden nun ausgeführt


for i in "${uninstallnames[@]}"
do
   adb shell monkey -p $i  -c android.intent.category.LAUNCHER 1 
    
done


echo Apps bleiben nun 20 sekunden ausgeführt....
sleep 20



echo Alle Apps werden wieder deinstalliert
for i in "${uninstallnames[@]}"
do
   adb uninstall $i
    
done


echo FINISHED



