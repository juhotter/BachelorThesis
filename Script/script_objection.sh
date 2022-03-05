#!sbin/sh
#zurNOT https://www.sisik.eu/apk-tool
ADB=/usr/bin/adb
#pip3 install objection 
#DOTO1: ALLE APPS MÜSSEN IM SELBEN VERZEICHNIS WIE DAS SCRIPT LIEGEN
#DOTO2: ALLE APK NAMEN EINTRAGEN UND LOS GEHTS ( hint: apk muss so heißen wie die app selbst für GREP )
#declare -a arr=( "slither.apk" "lulu.apk")
declare -a arr=( "slither.apk" "lulu.apk" )






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






################################HIER STARTET OBJECTION###########################
echo Handy signierte apks wieder vom Handy holen


declare -a pushnames=()
for i in "${onlynames[@]}"
do
    PACKAGENAME_TEMP=$(adb shell pm list packages -f -3 | cut -d "=" -f1 | grep $i)
    PUSHNAME_TEMP=$( echo $PACKAGENAME_TEMP | cut -d ":" -f 2) # ganzer pfad ohne package
    adb pull $PUSHNAME_TEMP


   #ONLYAPKNAME=$(echo $i | rev |cut -d "/" -f 1 | rev)  # base.apk bekommt man ; ist aber immer das selbe deswegen nicht nötig
   

   RANDOMFILENAME=$(uuidgen | tr -d '-')
   mv base.apk "${RANDOMFILENAME}.apk"
    pushnames+=("${RANDOMFILENAME}.apk")
done




#normale handy wieder weg
echo Alle Apps werden wieder deinstalliert
for i in "${uninstallnames[@]}"
do
   adb uninstall $i
    
done


#apps werden gepatched
declare -a onlyapknames=()
for i in "${pushnames[@]}"
do
  
   objection patchapk --source  $i
   onlyapknames+=($i)
done



#gepacthte werden wieder auf handy geladen
for i in "${onlyapknames[@]}" 
do
TEMP=$(echo $i  | cut -d "." -f 1) 
adb install  "${TEMP}.objection.apk"
rm "${TEMP}.objection.apk"
rm $i

done

echo alle objection geänderten apps sind nun am smartphone - am pc werden sie wieder gelöscht



#certificate pinning deaktivieren
for i in "${uninstallnames[@]}"
do
   objection -g $i run android sslpinning disable
   
done




#ausführen der objected apps
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