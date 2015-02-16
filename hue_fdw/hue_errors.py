#!/usr/bin/env python

## Table of the Error Codes that the Hue System might throw.
# http://www.developers.meethue.com/documentation/error-messages

hue_errors = { 
 1:   {'description' : 'unauthorized user', 
       'usage'       : """This will be returned if an invalid username is used in the request, or if the username does not have the rights to modify the resource."""},

 2:   {'description' : 'body contains invalid JSON',
       'usage'       : """This will be returned if the body of the message contains invalid JSON."""},

 3:   {'description' : 'resource, <resource>, not available',
       'usage'       : """This will be returned if the addressed resource does not exist. E.g. the user specifies a light ID that does not exist."""},

 4:   {'description' : 'method, <method_name>, not available for resource, <resource>',
       'usage'       : """This will be returned if the method (GET/POST/PUT/DELETE) used is not supported by the URL e.g. DELETE is not supported on the /config resource"""},

 5:   {'description' : 'missing parameters in body',
       'usage'       : """Will be returned if required parameters are not present in the message body. The presence of invalid parameters should not trigger this error as long as all required parameters are present."""},

 6:   {'description' : 'parameter, <parameter>, not available',
       'usage'       : """This will be returned if a parameter sent in the message body does not exist. This error is specific to PUT commands; invalid parameters in other commands are simply ignored."""},

 7:   {'description' : 'invalid value, <value>, for parameter, <parameter>',
       'usage'       : """This will be returned if the value set for a parameter is of the incorrect format or is out of range."""},

 8:   {'description' : 'parameter, <parameter>, is not modifiable',
       'usage'       : """This will be returned if an attempt to modify a read only parameter is made."""},

 11:  {'description' : 'too many items in list',
       'usage'       : """List in request contains too many items."""},

 12:  {'description' : 'Portal connection required',
       'usage'       : """Command requires portal connection. Returned if portalservices is false or the portal connection is down"""},

 901: {'description' : 'Internal error, <error code>',
       'usage'       : """This will be returned if there is an internal error in the processing of the command. This indicates an error in the bridge, not in the message being sent."""},

 101: {'description' : 'link button not pressed',
       'usage'       : """/config/linkbutton is false. Link button has not been pressed in last 30 seconds."""},

 110: {'description' : 'DHCP cannot be disabled',
       'usage'       : """DHCP can only be disabled if there is a valid static IP configuration."""},

 111: {'description' : 'Invalid updatestate',
       'usage'       : """checkforupdate can only be set in updatestate 0 and 1."""},

 201: {'description' : 'parameter, <parameter>, is not modifiable. Device is set to off.',
       'usage'       : """This will be returned if a user attempts to modify a parameter which cannot be modified due to current state of the device. This will most commonly be returned if the hue/sat/bri/effect/xy/ct parameters are modified while the on parameter is false."""},

 301: {'description' : 'group could not be created. Group table is full.', 
       'usage'       : """The bridge can store a maximum of 16 groups. This error will be returned if there are already the maximum number of groups created in the bridge."""},

 302: {'description' : "device, <id>, could not be added to group. Device group table is full.", 
       'usage'       : """The lamp can store a maximum of 16 groups. This error will be returned if the device cannot accept any new groups in its internal table.  Deprecated as of 1.4."""},

 304: {'description' : 'device, <id>, could not be added to the scene. Device is unreachable.',
       'usae'        : """This will be returned if an attempt to update a light list in a group or delete a group of type "Luminaire" or "LightSource". Note: as of 1.4."""},

 305: {'description' : 'It is not allowed to update or delete group of this type.',
       'usage'       : """This will be returned if an attempt to update a light list in a group or delete a group of type "Luminaire" or "LightSource". Note: as of 1.4."""},

 401: {'description' : 'scene could not be created. Scene creation in progress.',
       'usage'       : """This will be returned if a scene is activated which is currently still in the process of being created.  Deprecated as of 1.2.1"""},

 402: {'description' : 'Scene could not be created. Scene buffer in bridge full.',
       'usage'       : """It is not possible anymore to buffer scenes in the bridge for the lights. Application can try again later, let the user turn on lights or remove schedules."""},

 501: {'description' : 'No allowed to create sensor type',
       'usage'       : """Will be returned if the sensor type cannot be created using CLIP."""},

 502: {'description' : 'Sensor list is full.',
       'usage'       : """This will be returned if there are already the maximum number of sensors created in the bridge."""},

 601: {'description' : 'Rule engine full.',
       'usage'       : """Returned when already 100 rules are created and no further rules can be added."""},

 607: {'description' : 'Condition error',
       'usage'       : """Rule conditions contain errors or operator combination is not allowed (e.g. only one dt operator is allowed)"""},

 608: {'description' : 'Action error',
       'usage'       : """Rule actions contain errors or multiple actions with the same resource address."""},

 609: {'description' : 'Unable to activate',
       'usage'       : """Unable to set rule status to "enable", because rule conditions references unknown resource or unsupported resource attribute."""},

 701: {'description' : 'Schedule list is full.',
       'usage'       : """This will be returned if there are already the maximum number of schedules created in the bridge."""},

 702: {'description' : 'Schedule time-zone not valid.',
       'usage'       : """Cannot set parameter 'localtime', because timezone has not been configured."""},

 703: {'description' : 'Schedule cannot set time and local time.',
       'usage'       : """Cannot set parameter 'time' and 'localtime' at the same time."""},

 704: {'description' : 'Cannot create schedule',
       'usage'       : """Cannot create schedule because tag, <tag>, is invalid."""},

 705: {'description' : 'Cannot enable schedule, time is in the past.',
       'usage'       : """The schedule has expired, the time pattern has to be updated before enabling."""},

}

