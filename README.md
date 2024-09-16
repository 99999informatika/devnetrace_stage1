# DevNet Race 2020-2021 Stage 1
## Security Automation System from 99999 - Unified Automatic Endpoint Response

### Description
The application connects to a Cisco StealthWatch API and automatically handles alerts. It integrates Trend Micro and Cisco AMP for Endpoint.

Incoming StealthWatch alerts are checked on both endpoint managers through their APIs based on IP address. If the IP address is found in one of the databeses, it is isolated automatically.

The administrator can configure, start or stop the application through a web GUI.

![Diagram](/diagram.PNG)

### Business Outcome
- Application main purpose is to gain the security team efficiency with Automatic Response or Report system based on customized
netflow information (e.g. Blacklisted Host communication from endpoint)

### Re-usability
- Every customer who has Stealthwatch based analytics can use the application for basic alert, the API information can be provided by 
end-user on UI.

### Integration complexity
- „Front-End/User interface” for collect API information
- Backend contain:
    - Cisco: Stealthwatch, AMP4E, Webex Teams
    - 3rd party: Trend Micro: Apex Central

### OpenSource
- The system can run every platform with python based interpreters.

### Devnet References (how to use)
- SW: https://github.com/CiscoDevNet/stealthwatch-cloud-sample-scripts/blob/master/python/get_alerts.py
- AMP4E: https://github.com/CiscoDevNet/AMP-APIs-LLs
- Webex: https://github.com/CiscoDevNet/webexteamssdk

### Future proof
- Manual isolation option from the UI (under development)
- User based „Blacklisted hosts” information load with Stealthwatch API, from the UI
- Automatic collection of „Blacklisted hosts” information (RSS feed, collect information from cisco Talos blog etc…)
- Collect Flowmon based information
- Endpoint isolation with ISE, if the Endpoint protect