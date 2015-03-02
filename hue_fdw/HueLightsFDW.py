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
## This file has the one for the * Lights * in it.
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
            log_to_postgres('bridge IP address is required.', ERROR)

        if options.has_key('username'):
            self.userName = options['username']
        else:
            self.userName = 'postgreshue'
            log_to_postgres('Using Default Username:  postgreshue.', WARNING)

        self.baseURL = 'http://' + self.bridge + "/api/" + self.userName 

        # We don't really use this anywhere.  Including it for now in case it ends up having a use.
        if options.has_key('hueid'):
            self.hueID = options['hueid']
        else:
            self.hueID = None
            log_to_postgres('hueID not set', DEBUG)

        # Give the user a choice as to whether they want to serialize Dictionaries into 
        # HSTORE or JSON.  By default Multicorn serializes them to HSTORE.  (Issue #86 in the Multicorn Repo.)
        if options.has_key('kvType'):
            if options['kvType'].lower() in ['hstore', 'json']:
                self.kvType = options['kvType'].lower()
            else:
                log_to_postgres('Invalid Key Value Type: %s. (Choose "hstore" or "json")' % options['kvType'], ERROR)
        else:
            self.kvType = 'json'

        self.columns = columns

        self.mutable_columns = ['is_on', 
                                'hue', 
                                'color_mode', 
                                'effect', 
                                'alert', 
                                'xy', 
                               'reachable', 
                               'brightness', 
                               'saturation', 
                               'color_temperature']



    ############
    # SQL SELECT:
    # We get back all of the lights we can find and roll them up into rows
    def execute(self, quals, columns):

        log_to_postgres('Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Query Filters:  %s' % quals, DEBUG)

        # Question:  Is this really capped at 15 results per GET, or will it return everything?
        # ie, do we need to loop this until we exhaust all of the lights in the system, or is one GET enough?
        results = requests.get(self.baseURL + "/lights/")

        hueResults = json.loads(results.text)
         
        row = OrderedDict()
        for light in hueResults.keys():

            if 'light_id' in columns:
                row['light_id'] = int(light)

            if 'swversion' in columns:
                row['swversion'] = hueResults[light]['swversion']

            if 'unique_id' in columns:
                row['unique_id'] = hueResults[light]['uniqueid']

            if 'light_type' in columns:
                row['light_type'] = hueResults[light]['type']

            if 'model_id' in columns:
                row['model_id'] = hueResults[light]['modelid']

            # We are going to flatten out the "state" inner json.

            if 'is_on' in columns:
                row['is_on'] = hueResults[light]['state']['on']

            if 'hue' in columns:
                row['hue'] = hueResults[light]['state']['hue']

            if 'color_mode' in columns:
                row['color_mode'] = hueResults[light]['state']['colormode']

            if 'effect' in columns:
                row['effect'] = hueResults[light]['state']['effect']

            if 'alert' in columns:
                row['alert'] = hueResults[light]['state']['alert']

            if 'xy' in columns:
                row['xy'] = hueResults[light]['state']['xy']

            if 'reachable' in columns:
                row['reachable'] = hueResults[light]['state']['reachable']

            if 'brightness' in columns:
                row['brightness'] = hueResults[light]['state']['bri']

            if 'saturation' in columns:
                row['saturation'] = hueResults[light]['state']['sat']

            if 'color_temperature' in columns: 
                row['color_temperature'] = hueResults[light]['state']['ct']

            if 'pointsymbol' in columns:
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
            # Note:  Not sure how pointsymbol column filtering would work yet.
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
    def update(self, oldValues, newValues):

        #log_to_postgres('Update Request - old values:  %s' % oldValues, DEBUG)
        log_to_postgres('Update Request - new values:  %s' % newValues, DEBUG)

        # make sure we have the primary key to know which row to change
        if not oldValues.has_key('light id'):

             log_to_postgres('Update request requires light_id (The PK).  Missing From:  %s' % oldValues, ERROR)
         
        newState = {}
        for changedColumn in newValues.keys():

            if changeColumn != 'light_id':

                # We are only going to be able to change the "state" columns.
                if changeColumn not in self.mutable_columns:

                    log_to_postgres('Requested to change immutable column rejected:  %s' % changeColumn, ERROR)
    
                newState[changeColumn] = newValues[changedColumn]

        results = requests.put(self.BaseURL + '/%s/state' % oldValues['light_id'], newState)
 
        hueResults = json.loads(results.text)

        for status in hueResults:

              if not status.has_key('success'):

                    log_to_postgres('Column Update Failed for light_id %s:  %s' % (oldValues['light_id'], status), ERROR)
            
        return True

    ############
    # SQL INSERT:
    def insert(self, new_values):

        log_to_postgres('Insert Request Ignored - requested values:  %s' % new_values, DEBUG)

        return False

    ############
    # SQL DELETE
    # There really is nothing
    def delete(self, old_values):

        log_to_postgres('Delete Request Ignored - old values:  %s' % old_values, DEBUG)

        return False



