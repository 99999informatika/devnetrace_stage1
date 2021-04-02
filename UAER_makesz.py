#!/usr/bin/env python3
#This script is written by Tamas Z. Maklary contribution with 99999 Informatika Kft.
#The main purpuse of this pyscript is an unified endpoint response system with 
#Trend Micro Apex One, Cisco AMP for Endpoint , Stealthwatch, Webex Teams

import requests
import json
from flask import Flask, request, render_template, redirect, url_for
import os
import re


app = Flask(__name__)

@app.route('/')
def register():
    try:
        with open("start.txt" , "r") as fs0:
            proc_state = fs0.read()
        fs0.close()
        with open("automate.txt") as fs0:
            auto_state = fs0.read()
        fs0.close
    except:
        with open("start.txt" , "w") as fs0:
            proc_state = fs0.write('')
        fs0.close()
        with open("automate.txt" , 'w') as fs0:
            auto_state = fs0.write('')
        fs0.close

    if proc_state != 'started':
        logfiles = ['start.txt','automate.txt', 'webex_status.log', 'stealthwatch_status.log' ,'trend_micro_status.log', 'amp4e_status.log', 'message.txt']
        cfgfiles = ['tm', 'webex' , 'sw' , 'amp4e']
        for files in logfiles:
            with open(files , "w") as f:
                f.write('')
            f.close()
        for files in cfgfiles:
            with open(files+"_information.cfg" , "w") as f:
                f.write('')
            f.close()
        return render_template('register.html')
    elif auto_state == 'yes':
        return redirect('state_auto')
    else:
        return redirect('state_manual')
        

@app.route('/', methods=['POST'])
def form_post():
    #gathering informations from form
    vCSW_URL = request.form['CSW_URL']
    vCSW_USER = request.form['CSW_USER']
    vCSW_KEY = request.form['CSW_KEY']
    vTM_URL = request.form['TM_URL']
    vTM_APPID = request.form['TM_APPID']
    vTM_KEY = request.form['TM_KEY']
    vAMP4E_URL = request.form['AMP4E_URL']
    vAMP4E_CID = request.form['AMP4E_CID']
    vAMP4E_KEY = request.form['AMP4E_KEY']
    vWebex_TOKEN = request.form['Webex_TOKEN']
    #vWebex_ROOM = request.form['Webex_ROOM']
    #make the information to processable for write into file with is needed for the backend
    proc_CSW = [ '[StealthwatchCloud]' ,  'PORTAL_URL = ' + vCSW_URL , 'API_USER = ' + vCSW_USER , 'API_KEY = ' + vCSW_KEY ]
    proc_TM = ['[TrendMicro]' , 'PORTAL_URL = ' + vTM_URL , 'API_ID = ' + vTM_APPID , 'API_KEY = ' + vTM_KEY ]
    proc_AMP4E = ['[AMP4E]' , 'PORTAL_URL =' + vAMP4E_URL , 'API_CID = ' + vAMP4E_CID , 'API_KEY = ' + vAMP4E_KEY ]
    proc_Webex = ['[Webex]' , 'ACCESS_TOKEN = ' + vWebex_TOKEN ]
    with open("sw_information.cfg", "w") as f1:
        for proc in proc_CSW:
            f1.write('%s\n' % proc)
    
    f1.close()
    
    with open("tm_information.cfg", "w") as f2:
        for proc in proc_TM:
            f2.write('%s\n' % proc)
    
    f2.close()
    
    with open("amp4e_information.cfg", "w") as f3:
        for proc in proc_AMP4E:
            f3.write('%s\n' % proc)
        
    f3.close()
    
    with open("webex_information.cfg", "w") as f4:
        for proc in proc_Webex:
            f4.write('%s\n' % proc)
  
    f4.close()
  
    return redirect('integration')

@app.route('/integration/')
def integration():

    f1 = open("sw_information.cfg", "r")
    pCSW = f1.read()
    f1.close()
    f2 = open("tm_information.cfg", "r")
    pTM = f2.read()
    f2.close()
    f3 = open("amp4e_information.cfg", "r")
    pAMP4E = f3.read()
    f3.close()
    f4 = open("webex_information.cfg", "r")
    pWebex = f4.read()
    f4.close()
    
    with open("start.txt" , "r") as fss:
        started = fss.read()
    fss.close()

    if started != 'started':
        os.system('python3 start.py&')
        fs1 = open("start.txt" , "w")
        fs1.write('started')
        fs1.close()
    
    return render_template('registered.html', CSW=pCSW, TM=pTM, AMP4E=pAMP4E, Webex=pWebex)

@app.route('/state_auto/')
def auto():
    auto_operation = 'yes'
    with open("automate.txt" , "w") as fa1:
        fa1.write(auto_operation)
    fa1.close()
    with open("stealthwatch_status.log" , "r") as fo1:
        oCSW = fo1.read()
    fo1.close()

    with open("webex_status.log" , "r") as fo1:
        owebex = fo1.read()
    fo1.close()

    with open("message.txt", "r") as fmo1:
        message = fmo1.read()
    fmo1.close()

    with open("trend_micro_status.log" , "r") as fto1:
        oTM=fto1.read()
    fto1.close()

    with open("amp4e_status.log" , "r") as fo1:
        amp4e = fo1.read()
    fo1.close()

    #print(message)
    format_to_html = message.replace('\n' , '<br>')
    return render_template('state_auto.html' , CSW=oCSW , Webex=owebex , TM=oTM, AMP4E=amp4e, MSG=format_to_html)

@app.route('/state_manual/')
def manual():

    #auto_operation = 'no'
    auto_operation = 'yes'
    with open("automate.txt" , "w") as fa1:
        fa1.write(auto_operation)
    fa1.close()
    with open("stealthwatch_status.log" , "r") as fo1:
        oCSW = fo1.read()
    fo1.close()

    with open("webex_status.log" , "r") as fo1:
        owebex = fo1.read()
    fo1.close()

    with open("message.txt", "r") as fmo1:
        message = fmo1.read()
    fmo1.close()

    with open("trend_micro_status.log" , "r") as fto1:
        oTM=fto1.read()
    fto1.close()

    with open("amp4e_status.log" , "r") as fo1:
        amp4e = fo1.read()
    fo1.close()

    #print(message)
    format_to_html = message.replace('\n' , '<br>')
    return render_template('state_manual.html' , CSW=oCSW , Webex=owebex , TM=oTM, AMP4E=amp4e, MSG=format_to_html)

@app.route('/stop/')
def stop():
    with open("stop.txt", "w") as fso1:
        fso1.write("yes")
    fso1.close()
    fs1 = open("start.txt" , "w")
    fs1.write('stopped')
    fs1.close()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True , host='0.0.0.0' , port=8081 )
