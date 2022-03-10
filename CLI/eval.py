#!/usr/local/bin/python3
from cmath import log
from datetime import date
from email.policy import default
from itertools import count
import click
import logging
import subprocess
import json
import pandas

# no need for that - if mitmproxy 8.0 is public mode ( currently dev )
path_for_mitmproxy = "/Users/julianhotter/downloads/mitmproxy-main-osx/"

#./eval.py download fromfile FILENAME
#./eval.py run  (ungepatche apps runnen)
#./eval.py run --method METHODENNAME (ungepatche apps runnen)

proc = None


@click.command()
@click.argument('name', default='guest')
@click.option('--method',nargs=2,help='which method?')
@click.option('--fromfile',help='which file?')


def main(name,method,fromfile):

    
    

    if name == "evaluate":
        click.echo("Reading JSON FILE ...")
        parseJsonFile()
    if name == 'download':
            click.echo("reading package names...")
            parseTextFile(fromfile) 




    elif name == 'run':
        i = 0 
        if method[0] == "apkmitm":
            click.echo("You choose apkmitm patching with "+method[1])
            adbEnvironment(method[1])
            i+1
        elif method[0] == "objection":
            click.echo("You choose objection patching with"+method[1])
            adbEnvironment(method[1])
            i+1
        elif method[0] == "frida":
            click.echo("You choose frida patching with "+method[1])
            adbEnvironment(method[1])
            i+1
        elif  i == 0:
            click.echo("You choose without patching with " +method[1])
            adbEnvironment(method[1])




    


def parseTextFile(textname):
    datei = open(textname,'r')
    lines = datei.readlines()
    for i in lines:
        print(i.strip())
        subprocess.call("apkeep -a "+i.strip()+" .", shell=True )
    datei.close()



def adbEnvironment(apkfile):
    subprocess.run("adb devices", shell=True)
    subprocess.run("adb install "+apkfile,shell=True)
    packagename = apkfile[:len(apkfile)-4]
    print(packagename)
    subprocess.run("adb shell monkey -p "+packagename+" -c android.intent.category.LAUNCHER 1",shell=True) 
    subprocess.run("sleep 10", shell=True )
    subprocess.run("adb uninstall "+packagename,shell=True)
   
    
def startMitmProxy(appname):
    proc = subprocess.Popen(path_for_mitmproxy+"mitmdump -s tlslogger.py --set tls_logfile=tls-log.txt --set tls_tag="+appname+".apk",shell=True)
   
    
def endMitmProxy():
    print("Mitmproxy closes..")
    proc.kill()


#always parses tls-log.txt
def parseJsonFile():
    subprocess.run("cp tls-log.txt tls-log.json", shell=True)
    dataframe = pandas.read_json("tls-log.json", lines=True )
    print(dataframe)
    n_rows = dataframe.shape[0] # get rows ( how many traffic alltogether)
    #successcolumn_with = (dataframe['success'])
    

    




   
    

#entry point
if __name__ == "__main__":
    main()





