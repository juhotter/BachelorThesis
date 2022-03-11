#!/usr/local/bin/python3
from datetime import date
from email.policy import default
from itertools import count
import click
import logging
import subprocess
import json
import pandas

#REFERENCES:
# https://github.com/mitmproxy/android-unpinner
# https://github.com/shroudedcode/apk-mitm
# https://github.com/sensepost/objection


# no need for that - if mitmproxy 8.0 is public mode ( currently dev )
path_for_mitmproxy = "/Users/julianhotter/downloads/mitmproxy-main-osx/"
proc = None


#HOWTOUSE-CLI
#./eval.py download --fromfile FILENAME
#./eval.py evaluate 
#./eval.py run --method METHODENNAME NAME.APK ( apps runnen)
    # choose between -> apkmitm,objection,frida,none






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
    subprocess.run("adb shell monkey -p "+packagename+" -c android.intent.category.LAUNCHER 1",shell=True) 
    subprocess.run("adb shell monkey -p "+packagename+" --pct-touch 100 --throttle 10 500", shell = True)
    
    


def adb_uninstall_after_time(apkfile):
    subprocess.run("sleep 10", shell=True )
    packagename = apkfile[:len(apkfile)-4]
    subprocess.run("adb uninstall "+packagename,shell=True)




def startMitmProxy(appname):
    global proc 
    proc = subprocess.Popen(path_for_mitmproxy+"mitmdump -s tlslogger.py --set tls_logfile=tls-log.txt --set tls_tag="+appname,shell=True)
   
def endMitmProxy():
    click.echo("Mitmproxy closes..")
    global proc
    proc.kill()


#always parses tls-log.txt
def parseJsonFile():
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    click.echo(dataframe)
    n_rows = dataframe.shape[0] # get rows ( how many traffic alltogether got sniffed)
    


def apkmitm_patching(apkfile):
    subprocess.run("apk-mitm "+apkfile, shell = True)


def objection_patching(apkfile):
    subprocess.run("objection patchapk --source "+apkfile, shell = True)
    newapkname = apkfile[:len(apkfile)-4]+".objection.apk"
    packagename = apkfile[:len(apkfile)-4]
    adb_install(newapkname)
    subprocess.run("objection -g "+packagename+" run android sslpinning disable", shell = True)

  
def frida_patching(apkfile):
    subprocess.run("android-unpinner all "+apkfile,shell=True)
    

  










@click.command()
@click.argument('name')
@click.option('--method',nargs=2,help='which method -  choose between : none,apmitm,objection,frida?')
@click.option('--fromfile',help='which file?')


def main(name,method,fromfile):

    
    
    if name == "evaluate":
        click.echo("Reading JSON FILE ...")
        parseJsonFile()
    if name == 'download':
            click.echo("reading package names...")
            parseTextFile(fromfile) 




    elif name == 'run':
        startMitmProxy(method[1])
        if method[0] == "apkmitm":
            click.echo("You choose apkmitm patching with "+method[1])
            apkmitm_patching(method[1])
            newapkname = method[1][:len(method[1])-4]+"-patched.apk"
            adb_install(newapkname) # only install with new apk name
            adb_run((method[1]))
            adb_uninstall_after_time(method[1])
            endMitmProxy()
        
        elif method[0] == "objection":
            click.echo("You choose objection patching with"+method[1])
            objection_patching(method[1])
            adb_uninstall_after_time(method[1])
            endMitmProxy()
            


        elif method[0] == "frida":
            click.echo("You choose frida patching with "+method[1])
            frida_patching(method[1])
            endMitmProxy()


        elif  method[0] == "none":
            click.echo("You choose without patching with " +method[1])
            adb_install(method[1])
            adb_run(method[1])
            adb_uninstall_after_time(method[1])
            endMitmProxy()










#entry point
if __name__ == "__main__":
    main()





