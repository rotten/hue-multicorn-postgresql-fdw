################################################################################################################
## This is the implementation of the Multicorn ForeignDataWrapper class as an interface to the Philips Hue system
##
## We set up these endpoints:
##   * Lights
##   * Config
##   * Scenes
##   * Sensors
## as separate classes since they have very different structures and purposes.
## 
## Each of these FDW classes is in a different file.
## This file has the one for the * Lights * endpoint in it.
##
## R.Otten - 2015
################################################################################################################

from collections import OrderedDict
import json

from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG

import requests

from operatorFunctions import unknownOperatorException, getOperatorFunction


##############################################
## The Foreign Data Wrapper Class for Lights:
##
## Options:
##  bridge   -- Required:  The IP address for the Hue Bridge
##  username -- Required:  The API user name - configured when the bridge is set up 
##              (see http://www.developers.meethue.com/documentation/getting-started )
##  hueid    -- Optional:  The Hue system ID - not used at this time
##  kvtype   -- Optional:  json or hstore - Whether nested KV data returns JSON format or HSTORE format. (default:  json)
##  transitiontime -- Optional: Integer - Number of 100ms the bulb will take to transition during an update. (default: 4)
##
class HueLightsFDW(ForeignDataWrapper):

    """
    Philips Hue Lights Foreign Data Wrapper for PostgreSQL
    """

    def __init__(self, options, columns):

        super(HueLightsFDW, self).__init__(options, columns)

        log_to_postgres('options:  %s' % options, DEBUG)
        log_to_postgres('columns:  %s' % columns, DEBUG)

        if options.has_key('bridge'):
            self.bridge = options['bridge']
        else:
            log_to_postgres('bridge IP address is required for Hue Lights setup.', ERROR)

        if options.has_key('username'):
            self.userName = options['username']
        else:
            self.userName = 'postgreshue'
            log_to_postgres('Using Default Username for Hue Lights setup:  postgreshue.', WARNING)

        self.baseURL = 'http://' + self.bridge + "/api/" + self.userName + "/lights/"

        # We don't really use this anywhere.  Including it for now in case it ends up having a use.
        if options.has_key('hueid'):
            self.hueID = options['hueid']
        else:
            self.hueID = None
            log_to_postgres('hueID not set', DEBUG)

        # Give the user a choice as to whether they want to serialize Dictionaries into 
        # HSTORE or JSON.  By default Multicorn serializes them to HSTORE.  (Issue #86 in the Multicorn Repo.)
        if options.has_key('kvtype'):
            if options['kvtype'].lower() in ['hstore', 'json']:
                self.kvType = options['kvtype'].lower()
            else:
                log_to_postgres('Invalid Key Value Type for Hue Lights setup: %s. (Choose "hstore" or "json")' % options['kvType'], ERROR)
        else:
            self.kvType = 'json'

        # For now this is a global FDW setting.
        # It isn't a queryable data element on the lights endpoint, but rather an update option.
        # Since we can't really pass options in an update statement (that aren't columns), we'll set the
        # option on the FDW.
        if options.has_key('transitiontime'):
            self.transitionTime = int(options['transitiontime'])
        else:
            # The Hue System Default is '4' - which is 400ms.
            # We'll use that for our default here too.
            self.transitionTime = 4 

        ###
        # We need to identify the "primary key" column so we can do updates:
        self._row_id_column = 'light_id'

        # The columns we'll be using (defaults to 'all'):
        self.columns = columns

        # These are the only columns we are going to allow to be updated though:
        self.mutable_columns = ['is_on', 
                                'hue', 
                                'effect', 
                                'alert', 
                                'xy', 
                                'brightness', 
                                'saturation', 
                                'color_temperature']

        # We renamed some of the columns to avoid reserved PG keywords. (specifically "on" and "type")
        # While we were at it, we gave some of the columns more verbose names.
        self.columnKeyMap = { 'is_on'             : 'on',
                              'color_mode'        : 'colormode',
                              'brightness'        : 'bri',
                              'saturation'        : 'sat',
                              'color_temperature' : 'ct',
                              # 
                              'software_version'  : 'swversion',
                              'unique_id'         : 'uniqueid',
                              'model_id'          : 'modelid',
                              'light_type'        : 'type',
                              # These haven't been renamed:
                              'hue'               : 'hue',
                              'effect'            : 'effect',
                              'alert'             : 'alert', 
                              'xy'                : 'xy',
                              'reachable'         : 'reachable',
                              'pointsymbol'       : 'pointsymbol' }


    ############
    # We need to overload this function so Updates will work
    @property
    def rowid_column(self):
        return self._row_id_column


    ############
    # SQL SELECT:
    # We get back all of the lights we can find and roll them up into rows
    def execute(self, quals, columns):

        log_to_postgres('Hue Lights Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Hue Lights Query Filters:  %s' % quals, DEBUG)

        # Question:  Is this really capped at 15 results per GET, or will it return everything?
        # ie, do we need to loop this until we exhaust all of the lights in the system, or is one GET enough?
        results = requests.get(self.baseURL)

        hueResults = json.loads(results.text)
         
        row = OrderedDict()
        for light in hueResults.keys():

            # add the requested columns to the output:
            for column in columns:

                if column == 'light_id':
                    row['light_id'] = int(light)
                    continue

                if column == 'software_version':
                    row['software_version'] = hueResults[light]['swversion']
                    continue

                if column == 'unique_id':
                    row['unique_id'] = hueResults[light]['uniqueid']
                    continue

                if column == 'light_type':
                    row['light_type'] = hueResults[light]['type']
                    continue

                if column == 'model_id':
                    row['model_id'] = hueResults[light]['modelid']
                    continue

                # We are going to flatten out the "state" inner json.

                if column == 'is_on':
                    row['is_on'] = hueResults[light]['state']['on']
                    continue

                if column == 'hue':
                    row['hue'] = int(hueResults[light]['state']['hue'])
                    continue

                if column == 'color_mode':
                    row['color_mode'] = hueResults[light]['state']['colormode']
                    continue

                if column == 'effect':
                    row['effect'] = hueResults[light]['state']['effect']
                    continue

                if column == 'alert':
                    row['alert'] = hueResults[light]['state']['alert']
                    continue

                if column == 'xy':
                    row['xy'] = hueResults[light]['state']['xy']
                    continue

                if column == 'reachable':
                    row['reachable'] = hueResults[light]['state']['reachable']
                    continue

                if column == 'brightness':
                    row['brightness'] = int(hueResults[light]['state']['bri'])
                    continue

                if column == 'saturation':
                    row['saturation'] = int(hueResults[light]['state']['sat'])
                    continue

                if column == 'color_temperature': 
                    row['color_temperature'] = int(hueResults[light]['state']['ct'])
                    continue

                if column == 'pointsymbol':
                    # Pointsymbol isn't used by the API yet.  We'll save it as is for now.
                    # HSTORE Column Type:
                    if self.kvType == 'hstore':
                        row['pointsymbol'] = hueResults[light]['pointsymbol']
                    # JSON Column Type:
                    else:  
                        row['pointsymbol'] = json.dumps(hueResults[light]['pointsymbol'])


            # Unfortunately the Hue API doesn't have much in the way of filtering when you get the data.
            # So we do it here.
            # We can't have more than 63 lights in one system, and we only have 15 columns to worry about.
            # Note:  Not sure how pointsymbol column filtering would work yet, nor xy column!
            goodRow = True
            for qual in quals:

                try:

                    operatorFunction = getOperatorFunction(qual.operator)

                except unknownOperatorException, e:

                    log_to_postgres(e, ERROR)

                # The SQL parser should have caught if the where clause referenced a column we aren't selecting.
                # If it didn't, we'll just let this next statement throw an exception (rather than trying to handle it).
                if not operatorFunction(row[qual.field_name], qual.value):

                    # this column  didn't match.  Drop out and then move to the next row
                    goodRow = False
                    break

            if goodRow:

                yield row
 
             # otherwise, loop around and try the next row


    ############
    # SQL UPDATE:
    ## -- we should consider implementing 'rollback' (and, necessarily, 'commit')
    def update(self, lightID, newValues):

        log_to_postgres('Hue Lights Update Request - lightID:  %s' % lightID, DEBUG)
        log_to_postgres('Hue Lights Update Request - new values:  %s' % newValues, DEBUG)

        newState = {}
        for changedColumn in newValues.keys():

            # We are only going to be able to change the "state" columns.
            if changedColumn in self.mutable_columns:

                # 't' and 'f' are only going to show up on the boolean columns
                if newValues[changedColumn] == 't':
                    newState[self.columnKeyMap[changedColumn]] = True
                elif newValues[changedColumn] == 'f':  
                    newState[self.columnKeyMap[changedColumn]] = False
                else:
                    newState[self.columnKeyMap[changedColumn]] = newValues[changedColumn]

        newState['transitiontime'] = self.transitionTime

        log_to_postgres(self.baseURL + '%s/state' % lightID + ' -- ' + json.dumps(newState), DEBUG)
        results = requests.put(self.baseURL + '%s/state' % lightID, json.dumps(newState))
        
        try:

            hueResults = json.loads(results.text)

        except Exception, e:

            log_to_postgres('Unexpected (non-JSON) response from the Hue Bridge: %s' % self.bridge, ERROR)
            log_to_postgres('%s' % e, ERROR)
            log_to_postgres('%s' % results, ERROR)
    

        for status in hueResults:

              if not status.has_key('success'):

                    log_to_postgres('Hue Lights Full Results: %s' % results.text, DEBUG)
                    log_to_postgres('Hue Lights Column Update Failed for light_id %s:  %s' % (lightID, status), ERROR)
            

    ############
    # SQL INSERT:
    def insert(self, new_values):

        log_to_postgres('Hue Lights Insert Request Ignored - requested values:  %s' % new_values, WARNING)


    ############
    # SQL DELETE
    # There really is nothing
    def delete(self, old_values):

        log_to_postgres('Hue Lights Delete Request Ignored - old values:  %s' % old_values, WARNING)



