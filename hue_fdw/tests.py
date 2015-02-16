#!/usr/bin/env python

## scripts to "play with" the Hue api before putting them into an FDW.

import sys
import requests
import json
import time

hueID = '001788fffe1782e3'
#hueHost = 'http://192.168.30.116'
hueHost = 'http://192.168.200.118'
hueUser = 'postgreshue'


####
lightsURL = hueHost + '/api/' + hueUser + '/lights'
hues = requests.get(lightsURL)

print lightsURL
print hues.status_code
print json.dumps(hues.json(), indent=4)
print

####
groupsURL = hueHost + '/api/' + hueUser + '/groups'
hues = requests.get(groupsURL)

print groupsURL
print hues.status_code
print json.dumps(hues.json(), indent=4)

####
configURL = hueHost + '/api/' + hueUser + '/config'
hues = requests.get(configURL)

print configURL
print hues.status_code
print json.dumps(hues.json(), indent=4)

####
schedulesURL = hueHost + '/api/' + hueUser + '/schedules'
hues = requests.get(schedulesURL)

print schedulesURL
print hues.status_code
print json.dumps(hues.json(), indent=4)

####
scenesURL = hueHost + '/api/' + hueUser + '/scenes'
hues = requests.get(scenesURL)

print scenesURL
print hues.status_code
print json.dumps(hues.json(), indent=4)

####
sensorsURL = hueHost + '/api/' + hueUser + '/sensors'
hues = requests.get(sensorsURL)

print sensorsURL
print hues.status_code
print json.dumps(hues.json(), indent=4)

####
rulesURL = hueHost + '/api/' + hueUser + '/rules'
hues = requests.get(rulesURL)

print rulesURL
print hues.status_code
print json.dumps(hues.json(), indent=4)

#sys.exit(0)

hues = requests.put(lightsURL + '/1/state', '{"on": false}')
time.sleep(1)
hues = requests.put(lightsURL + '/2/state', '{"on": false}')
time.sleep(1)
hues = requests.put(lightsURL + '/3/state', '{"on": false}')
#print hues.status_code
#print hues.text
time.sleep(1)

hues = requests.put(lightsURL + '/1/state', '{"on": true, "sat":255, "bri":255, "effect":"none"}')
hues = requests.put(lightsURL + '/1/state', '{"on": true, "sat":255, "bri":255, "effect":"none"}')
hues = requests.put(lightsURL + '/1/state', '{"on": true, "sat":255, "bri":255, "effect":"none"}')
sys.exit(0)

hues = requests.put(lightsURL + '/1/state', '{"on": true, "sat":255, "bri":255, "effect":"colorloop"}')
time.sleep(10)
hues = requests.put(lightsURL + '/2/state', '{"on": true, "sat":255, "bri":255, "effect":"colorloop"}')
time.sleep(10)
hues = requests.put(lightsURL + '/3/state', '{"on": true, "sat":255, "bri":255, "effect":"colorloop"}')
print hues.status_code
print hues.text

#h = 0
#while h < 65535:

    #hues = requests.put(lightsURL + '/1/state', '{"hue":%d}' % h)
    #time.sleep(.1)

    #hues = requests.put(lightsURL + '/2/state', '{"hue":%d}' % h)
    #time.sleep(.1)

    #hues = requests.put(lightsURL + '/3/state', '{"hue":%d}' % (h + 1000))
    #time.sleep(.5)

    #h += 500

