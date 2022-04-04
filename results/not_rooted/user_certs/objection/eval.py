#!/usr/local/bin/python3
from datetime import date
from email.policy import default
from itertools import count
from multiprocessing.connection import wait
from sre_constants import SUCCESS
from tokenize import group
import click
import logging
import subprocess
import json
import pandas
import matplotlib.pyplot as plt
import packaging
import random
import time




#version3 = automatisch 
#version2 = manuell
#version1 = einfach starten und beenden.


#REFERENCES:
# https://github.com/mitmproxy/android-unpinner
# https://github.com/shroudedcode/apk-mitm
# https://github.com/sensepost/objection


# no need for that - if mitmproxy 8.0 is public mode ( currently dev )
path_for_mitmproxy = "/Users/julianhotter/downloads/mitmproxy-main-osx/"
proc = None
model = "Test"
start = None


#HOWTOUSE-CLI
#./eval.py download --fromfile FILENAME
#./eval.py evaluate 
#./eval.py run --method METHODENNAME NAME.APK ( apps runnen)
    # choose between -> apkmitm,objection,frida,none,rooted



#./eval.py run --method rooted com.instagram.android.apk


def parseTextFile(textname):
    datei = open(textname,'r')
    lines = datei.readlines()
    for i in lines:
        click.echo(i.strip())
        subprocess.call("apkeep -a "+i.strip()+" .", shell=True )
    datei.close()



def adb_install(apkfile):
    subprocess.run("adb devices", shell=True)
    subprocess.run("adb install "+apkfile,shell=True)
    

def adb_run(apkfile):
    packagename = apkfile[:len(apkfile)-4]
    click.echo(packagename)
    subprocess.run("adb shell monkey -p "+packagename+" -c android.intent.category.LAUNCHER 1  ",shell=True) #auskommentieren für frida alleine
    subprocess.Popen("objection explore --startup-command 'android sslpinning disable'", shell = True)
    subprocess.run("adb push  monkey.sh /data/local/tmp/monkey.sh",shell = True)
    subprocess.run("adb shell chmod +x /data/local/tmp/monkey.sh",shell = True)
    global start
    start = time.time()
    subprocess.run("adb shell /data/local/tmp/monkey.sh", shell = True)

    
    


def adb_uninstall_after_time(apkfile):
    #subprocess.run("sleep 20", shell=True )
    
    packagename = apkfile[:len(apkfile)-4]
    subprocess.run("adb uninstall "+packagename,shell=True)
    global start
    time.sleep(max(0, start - time.time() + 30))




def startMitmProxy(appname,method):
    global proc 
    #global model
    #model = subprocess.run("adb devices -l |  rev |  cut -d ' ' -f 3 | rev | grep model",shell = True) 
    #proc = subprocess.Popen(path_for_mitmproxy+"mitmdump -s tlslogger.py --set tls_logfile=tls-log.txt --set tls_tag="+appname,shell=True)

    #arg1 = "tls_app="+appname
    #arg2 = "tls_method="+methodtart
    #arg3 = "tls_device="+str(model)
    #fullpath = path_for_mitmproxy+"mitmdump"

    newappname = appname[:len(appname)-4]

    #### HIER ANDEREN APPNAMEN MITGEBEN EINFACH - NICHT PACKAGE
    #proc =subprocess.Popen([fullpath, "-s", "tlslogger.py", "--set", "tls_logfile=tls-log.txt", "--set", arg1, "--set", arg2, "--set", arg3 ],shell=True)
    proc = subprocess.Popen(path_for_mitmproxy+"mitmdump -s tlslogger.py --set tls_logfile=tls-log.txt --set tls_app="+newappname+" --set tls_method="+method+" --set tls_device=ONEPLUS_A6003 --set tls_downloadgroup=Million_bis_Milliarde",shell=True)
#/Users/julianhotter/downloads/mitmproxy-main-osx/mitmdump -s tlslogger.py --set tls_logfile=tls-log.txt --set tls_app=appname --set tls-method=method --set tls_device=device  --set tls_downloadgroup=>1Milliarde




def endMitmProxy():
    click.echo("Mitmproxy closes..")
    global proc
    proc.terminate()


#always parses tls-log.txt
def parseJsonFile2(): #ganz genau nach einzelne apps
    global model
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    #click.echo(dataframe)
    all_app_names = sorted(dataframe['app'].unique())
    #grouped = dataframe.groupby('app')["success"].value_counts(normalize=True).mul(10).unstack().sort_index(ascending=False)
    grouped = dataframe.groupby('app')["method","success"].value_counts().unstack().sort_index(ascending=False)
    #print(grouped)
    ax = grouped.plot.barh(stacked=True,color=['wheat', 'gold','black','red'])
    ax.set_title('Vergleich der Approaches gruppiert nach Apps -  Device: '+model)
    ax.set_xlabel('contacted domains')
    ax.set_ylabel('')
    ax.plot()
    plt.show()
    #https://matplotlib.org/stable/gallery/color/named_colors.html
    

def parseJsonFile(): #aggregiert in pro gruppe oder methode oderso
    global model
    model = "Oneplus 6 - Android 11 "
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    n = len(dataframe)
    n_false=(dataframe.groupby("success")["success"].count()).tolist()[0]
    n_true=(dataframe.groupby("success")["success"].count()).tolist()[1]
    percentage_true = ((n_true/n)*100) # percentage of true from all 

    
    new_df = pandas.DataFrame([
                    (n_true, n_false, percentage_true),
    
                   
                   ('The Square', 65, 25.30)],
           columns=('True', 'False', 'Percentage')
                 )
    
    print(new_df)


    grouped = dataframe.groupby('version')["success",].value_counts().unstack()
    ax = grouped.plot.barh(stacked=True,color=['darkred', 'gold','black','red'])
    ax.set_title("Vergleich: keine Interaktion - Manuell -  Automatisch")
    ax.set_xlabel('Contacted Domains')
    ax.plot()
    plt.show()
   

    
   
    


def apkmitm_patching(apkfile):
    subprocess.run("apk-mitm "+apkfile, shell = True)


def objection_patching(apkfile,method):
   
    subprocess.run("objection patchapk --source "+apkfile, shell = True)
    startMitmProxy(apkfile,method)
    print("waiting for mitmproxy to set up")
    time.sleep(10) # wait untill mitmproxy is up 
    newapkname = apkfile[:len(apkfile)-4]+".objection.apk"
    packagename = apkfile[:len(apkfile)-4]
    
    adb_install(newapkname)



  
def frida_patching(apkfile):
    subprocess.run("android-unpinner all "+apkfile,shell=True)
    

  










@click.command()
@click.argument('name')
@click.option('--method',nargs=2,help='which method -  choose between : none,apmitm,objection,frida,rooted?')
@click.option('--fromfile',help='which file?')


def main(name,method,fromfile):

    
    
    if name == "evaluate":
        click.echo("Reading JSON FILE ...")
        parseJsonFile2()
    if name == 'download':
            click.echo("reading package names...")
            parseTextFile(fromfile) 




    elif name == 'run':
        
        if method[0] == "apkmitm":
            startMitmProxy(method[1],method[0])
            click.echo("You choose apkmitm patching with "+method[1])
            apkmitm_patching(method[1])
            newapkname = method[1][:len(method[1])-4]+"-patched.apk"
            adb_install(newapkname) # only install with new apk names
            adb_run((method[1]))
            adb_uninstall_after_time(method[1])
            endMitmProxy()
        
        elif method[0] == "objection":
            
            click.echo("You choose objection patching with"+method[1])
            objection_patching(method[1],method[0])
            
            adb_run((method[1]))
            
            adb_uninstall_after_time(method[1])
            endMitmProxy()
            


        elif method[0] == "frida":
            click.echo("You choose frida patching with "+method[1])
            startMitmProxy(method[1],method[0])
            frida_patching(method[1])
            adb_run(method[1])
            adb_uninstall_after_time(method[1])
            endMitmProxy()


        elif  method[0] == "none":
            startMitmProxy(method[1],method[0])
            click.echo("You choose without patching with " +method[1])
            adb_install(method[1])
            adb_run(method[1])
            adb_uninstall_after_time(method[1])
            endMitmProxy()
        
        elif  method[0] == "rooted":
            startMitmProxy(method[1],method[0])
            click.echo("You choose without patching on a rooted device " +method[1])
            adb_install(method[1])
            adb_run(method[1])
            adb_uninstall_after_time(method[1])
            endMitmProxy()








#entry point
if __name__ == "__main__":
    main()





