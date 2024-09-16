#!/usr/bin/env python3

import os
import requests
import time
import schedule
import json
import configparser
import re
import hashlib
import jwt
import base64
from Crypto.PublicKey import RSA
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

config = configparser.ConfigParser()
isolate_system = ''
resolved = ['']

with open("stop.txt" , "w") as fs0:
    fs0.write("no")
fs0.close()   

def create_checksum(http_method, raw_url, headers, request_body):
    """Creates a base64_string from the provided parameters"""
    string_to_hash = http_method.upper() + '|' + raw_url.lower() + '|' + headers + '|' + request_body    
    base64_string = base64.b64encode(hashlib.sha256(str.encode(string_to_hash)).digest()).decode('utf-8')
    return base64_string    
    
def create_jwt_token(appication_id, api_key, http_method, raw_url, headers, request_body,
                     iat=time.time(), algorithm='HS256', version='V1'):
    """Returns a jwt token with the paramteres"""
    checksum = create_checksum(http_method, raw_url, headers, request_body)
    payload = {'appid': appication_id,
               'iat': iat,
               'version': version,
               'checksum': checksum}
    token = jwt.encode(payload, api_key, algorithm=algorithm).decode('utf-8')
    return token

def TM_search(ininfo):
    """
    Searches for IP address on Trend Micro server

    ininfo: ip address to search;
    Reads config from tm_information.cfg;
    Connects to API, returns security agent with matchig ip
    """
    config.read("tm_information.cfg") 
    if config["TrendMicro"]["PORTAL_URL"] != '':
        use_url_base = 'https://' + config["TrendMicro"]["PORTAL_URL"] +':443'
        use_application_id = config["TrendMicro"]["API_ID"]
        use_api_key = config["TrendMicro"]["API_KEY"]
        productAgentAPIPath = '/WebApp/API/AgentResource/ProductAgents'
        useQueryString = '?ip_address=' + ininfo
        useRequestBody = ''
        canonicalRequestHeaders = ''
        jwt_token = create_jwt_token(use_application_id, use_api_key, 'GET',
                                    productAgentAPIPath + useQueryString,
                                    canonicalRequestHeaders, useRequestBody, iat=time.time())
        headers = {'Authorization': 'Bearer ' + jwt_token}
        try:
            r = requests.get(use_url_base + productAgentAPIPath + useQueryString, headers=headers, data=useRequestBody, verify=False)
            TM_code = r.status_code
        except:
            TM_code = 429
        if TM_code < 299:
            TM_status = str(TM_code) + ' ' + 'OK'
            with open('trend_micro_status.log' , "w") as f1:
                f1.write('%s' % TM_status)
            f1.close()
            results = json.loads(r.content)['result_content']
            #print(results)        
            for result in results:
                #Processes only the first result (should only be one)
                entity = result['entity_id']
                #print(entity)
                return entity
        else:
            TM_status =  str(TM_code)  + ' ' + 'Error'
            with open('trend_micro_status.log' , "w") as f1:
                f1.write('%s' % TM_status)
            f1.close()
            return 'None'
        #print(r.json()['result_code'])
        #print(r.json()['result_description'])
        #print(r.json()['result_content'])
    else:
        TM_status = 'Not Provided'
        with open('trend_micro_status.log' , "w") as f1:
            f1.write('%s' % TM_status)
        f1.close()
        return 'None'

def AMP4E_search(ipv4):
    """
    Searches for IP address on Cisco AMP for Endpoint server

    ipv4: ipv4 address;
    Reads config from amp4e_information.cfg;
    Connects to API, returns security agent with matchig ip
    """
    config.read("amp4e_information.cfg")
    host=config["AMP4E"]["PORTAL_URL"]
    client_id=config["AMP4E"]["API_CID"]
    api_key=config["AMP4E"]["API_KEY"]
    connector_guid = ''
    request_headers = {
            "Content-Type" : "application/json",
            "Accept" : "application/json",
            "Authorization" : "Basic"
        }
    if host != '':
        url = f"https://{client_id}:{api_key}@{host}/v1/computers?internal_ip=" + ipv4
        try:
            response = requests.get(url, headers=request_headers, verify=False)
        except:
            AMP4E_status = 404
        #response.raise_for_status()
        #print(response.status_code)
        if response.status_code == 200:
            AMP4E_status = str(response.status_code) + ' OK'
            #print(response.status_code)
            result = response.json()['data']
            #print(ipv4)
            for ip in result:
                #Processes only the last result (should only be one)
                #print((ip['connector_guid']))
                connector_guid = ip['connector_guid']
            
            with open("amp4e_status.log", "w") as f1:
                f1.write('%s' % AMP4E_status)
            f1.close()

            if connector_guid != "":
                return connector_guid
            else:
                return 'None'
        else:
            AMP4E_status = str(response.status_code) + ' Error'
            with open("amp4e_status.log", "w") as f1:
                f1.write('%s' % AMP4E_status)
            f1.close()
            return 'None'
    else:
        AMP4E_status = 'Not Provided'
        with open ('apm4e_status.log' , "w") as f1:
            f1.write('%s' % AMP4E_status )
        f1.close()
        return 'None'

def swcloud_api():
    """
    Gets Alerts from server

    Reads configuration from sw_information.cfg;
    Connects to API with ApiUser and ApiKey;
    Response 200: Returns http response body (alerts)
    """
    config.read("sw_information.cfg")
    if config["StealthwatchCloud"]["PORTAL_URL"] != '':
        url = "https://" + config["StealthwatchCloud"]["PORTAL_URL"] + "/api/v3/alerts/alert/"
        authorization = "ApiKey " + config["StealthwatchCloud"]["API_USER"] + ":" + config["StealthwatchCloud"]["API_KEY"]
        request_headers = {
            "Content-Type" : "application/json",
            "Accept" : "application/json",
            "Authorization" : authorization
        }
        api_session = requests.Session()
        response = api_session.request("GET", url, headers=request_headers, verify=False)
        if (response.status_code == 200):
            SW_status = str(response.status_code) + '\t' + 'OK'
            with open('stealthwatch_status.log' , "w") as f1:
                f1.write('%s' % SW_status)
            f1.close()
            alerts = json.loads(response.content)["objects"]
            return  alerts
        else:
            SW_status = str(response.status_code) + '\t' + 'Error'
            with open('stealthwatch_status.log' , "w") as f1:
                f1.write('%s' % SW_status)
            f1.close()
            return "An error has ocurred, while fetching alerts, with the following code {}".format(response.status_code)
    else:
        SW_status = 'Not Provided'
        with open('stealthwatch_status.log' , "w") as f1:
            f1.write('%s' % SW_status)
        f1.close()
        return 'Stealthwatch API not provided'        

def send_message(message):
    """wirtes message parameter in "message.txt"""
    with open("message.txt","a") as fm1:
        fm1.write('%s\n' % message)
    fm1.close()

    config.read("webex_information.cfg")
    if config["Webex"]["ACCESS_TOKEN"] != '':
        url = "https://webexapis.com/v1/webhooks/incoming/" + config["Webex"]["ACCESS_TOKEN"]
        texttowebex =  message
        payload = {
        'text': texttowebex
        }
        files = [

        ]
        headers = {
        'Accept': 'application/json'
        }
        responsewebex = requests.request("POST", url, headers=headers, data = payload, files = files)
        
        if responsewebex.status_code == 204:
            webex_status = str(responsewebex.status_code) + '\t ' + 'OK'
        else:
            webex_status = str(responsewebex.status_code) + '\t' + 'Error'

        with open('webex_status.log' , "w") as f1:
            f1.write('%s' % webex_status)
        f1.close()
        
        return
    else:
        webex_status = 'Not Provided'
        with open('webex_status.log' , "w") as f1:
            f1.write('%s' % webex_status)
        f1.close()
        return
    
def search_host(ipv4):
    """Categorises ipv4 addess based on API searches"""
    if str(TM_search(ipv4)) != 'None':
        return 'TM'
    elif AMP4E_search(ipv4) != 'None':
        return 'AMP'
    else:
        return 'NoS'



def TM_isolate(identity, ipv4):
    """Isolates security agent on Trend Micro based on parameters"""
    config.read("tm_information.cfg") 
    if config["TrendMicro"]["PORTAL_URL"] != '':
        use_url_base = 'https://' + config["TrendMicro"]["PORTAL_URL"] +':443'
        use_application_id = config["TrendMicro"]["API_ID"]
        use_api_key = config["TrendMicro"]["API_KEY"]
        productAgentAPIPath = '/WebApp/API/AgentResource/ProductAgents'
        useQueryString = '?ip_address=' + ipv4
        useRequestBody = ''
        canonicalRequestHeaders = ''
        useRequestBody = json.dumps({'entity_id': identity, 'act': 'cmd_isolate_agent', 'allow_multiple_match': False})
        jwt_token = create_jwt_token(use_application_id, use_api_key, 'POST',
                                    productAgentAPIPath + useQueryString,
                                    canonicalRequestHeaders, useRequestBody, iat=time.time())
        headers = {'Authorization': 'Bearer ' + jwt_token}
        try:
            r = requests.post(use_url_base + productAgentAPIPath + useQueryString, headers=headers, data=useRequestBody, verify=False)
            TM_status = r.status_code
        except:
            TM_status = 429
        if TM_status < 299:
            TM_status = str(r.status_code) + ' ' + 'OK'
            with open('trend_micro_status.log' , "w") as f1:
                f1.write('%s' % TM_status)
            f1.close()
            results = json.loads(r.content)['result_content']
            #print(results)        
            for result in results:
                #Processes only the first result (should only be one)
                entity = result['entity_id']
                #print(entity)
                return entity
        else:
            TM_status = str(r.status_code) + ' ' + 'Error'
            with open('trend_micro_status.log' , "w") as f1:
                f1.write('%s' % TM_status)
            f1.close()
        #print(r.json()['result_code'])
        #print(r.json()['result_description'])
        #print(r.json()['result_content'])
    else:
        TM_status = 'Not Provided'
        with open('trend_micro_status.log' , "w") as f1:
            f1.write('%s' % TM_status)
        f1.close()
        return 'None'

def AMP4E_isolate(identitiy):
    """Isolates security agent on Cisco AMP for Endpoint based on parameters"""
    config.read("amp4e_information.cfg")
    host=config["AMP4E"]["PORTAL_URL"]
    client_id=config["AMP4E"]["API_CID"]
    api_key=config["AMP4E"]["API_KEY"]
    request_data = {
        "comment" : "This is an automatic isolation progress based on Stealthwatch information",
        "unlock_code" : "unlockme"
        }
    if host != '':
        url = f"https://{client_id}:{api_key}@{host}/v1/computers/" + identitiy + "/isolation"
        #print(url)
        response = requests.put(url, data=request_data, verify=False)
        #response.raise_for_status()
        #print(response.status_code)
        if response.status_code == 200:
            AMP4E_status = str(response.status_code) + ' OK'
            with open("amp4e_status.log", "w") as f1:
                f1.write('%s' % AMP4E_status)
            f1.close()
            return response.status_code
        else:
            AMP4E_status = str(response.status_code) + ' Error'
            with open("amp4e_status.log", "w") as f1:
                f1.write('%s' % AMP4E_status)
            f1.close()
            return response.status_code
    else:
        AMP4E_status = 'Not Provided'
        with open("amp4e_status.log", "w") as f1:
            f1.write('%s' % AMP4E_status)
        f1.close()
        return AMP4E_status

def wait_for_user_request():
    return 'VALAMI'

ipv4 = ''
handled = []
while True:
    #TODO: Ez nem volt felhasználva sehol
    #with open("automate.txt" , "r") as fauto:
    #    automate = fauto.read()
    #fauto.close()
    swcloud_datas = swcloud_api()
    if swcloud_datas != 'Stealthwatch API not provided':
        for alert in swcloud_datas:
            text = alert['text']
            ips = alert['source_info']['ips']
            for ip in ips:
                #Processes only the last result (should only be one)
                ipv4 = ip
            proc = str(text)  + ' , ' + str(ip)
            exp = re.search('^User', proc)
            if exp:
                if ipv4 not in handled:
                    send_message('Blacklisted host communication alert:\n' + proc)
                    isolate = search_host(ipv4)
                    if isolate == 'TM':
                        #print(TM_search(ipv4))
                        TM_isolate(TM_search(ipv4), ipv4)
                        handled.append(ipv4)
                        send_message(ipv4 + ' is isolated with Trend Micro')
                    elif isolate == 'AMP':
                        #print(AMP4E_search(ipv4))
                        test = AMP4E_isolate(AMP4E_search(ipv4))
                        handled.append(ipv4)
                        if test == 200:
                            send_message(ipv4 + ' is isolated with Cisco AMP for Endpoint')
                        elif test == 409:
                            send_message(ipv4 + ' has already isolated with Cisco AMP for Endpoint')
                        else:
                            send_message(ipv4 + ' something went wrong this IP, error code is:' + test)
        
                    else:
                        send_message('There is no Endpoint Security Solution for IP: ' + ipv4)
                        handled.append(ipv4) 
    else:
        with open("message.txt","w") as fm1:
            fm1.write('%s\n' % swcloud_datas)
        fm1.close()

    with open("stop.txt" , "r") as fs1:
        stop_variable = fs1.read()
    fs1.close()
    time.sleep(10)
    if stop_variable == "yes":
        with open("start.txt", "w") as fs1:
            fs1.write('stopped')
        fs1.close
        break