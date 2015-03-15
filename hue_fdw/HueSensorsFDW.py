################################################################################################################
## This is the implementation of the Multicorn ForeignDataWrapper class as an interface to the Philips Hue system
##
## We set up these endpoints:
##   * Lights
##   * Sensors
##   * Scenes
##   * Sensors
## as separate classes since they have very different structures and purposes.
## 
## Each of these FDW classes is in a different file.
## This file has the one for the * Sensors * endpoint in it.
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
## The Foreign Data Wrapper Class for Sensors:
##
## Options:
##  bridge   -- Required:  The IP address for the Hue Bridge
##  username -- Required:  The API user name - configured when the bridge is set up 
##              (see http://www.developers.meethue.com/documentation/getting-started )
##  hueid    -- Optional:  The Hue system ID - not used at this time
##  kvtype   -- Optional:  json or hstore - Whether nested KV data returns JSON format or HSTORE format. (default:  json)
##
## ** We do not yet support creating new sensors with this foreign data wrapper. **
##
class HueSensorsFDW(ForeignDataWrapper):

    """
    Philips Hue Lights Foreign Data Wrapper for PostgreSQL
    """

    def __init__(self, options, columns):

        super(HueSensorsFDW, self).__init__(options, columns)

        log_to_postgres('Hue Sensors options:  %s' % options, DEBUG)
        log_to_postgres('Hue Sensors columns:  %s' % columns, DEBUG)

        if options.has_key('bridge'):
            self.bridge = options['bridge']
        else:
            log_to_postgres('bridge IP address is required for Hue Sensors setup.', ERROR)

        if options.has_key('username'):
            self.userName = options['username']
        else:
            self.userName = 'postgreshue'
            log_to_postgres('Using Default Username for Hue Sensors setup:  postgreshue.', WARNING)

        self.baseURL = 'http://' + self.bridge + "/api/" + self.userName + "/sensors/"

        # We don't really use this anywhere.  Including it for now in case it ends up having a use.
        if options.has_key('hueid'):
            self.hueID = options['hueid']
        else:
            self.hueID = None
            log_to_postgres('hueID not set in Hue Sensors setup', DEBUG)

        # Give the user a choice as to whether they want to serialize Dictionaries into 
        # HSTORE or JSON.  By default Multicorn serializes them to HSTORE.  (Issue #86 in the Multicorn Repo.)
        if options.has_key('kvtype'):
            if options['kvtype'].lower() in ['hstore', 'json']:
                self.kvType = options['kvtype'].lower()
            else:
                log_to_postgres('Invalid Key Value Type for Hue Sensors setup: %s. (Choose "hstore" or "json")' % options['kvType'], ERROR)
        else:
            self.kvType = 'json'

        ###
        # Make note of the "primary key" column to support updates.
        self._row_id_column = 'sensor_id'

        # The columns we'll be using (defaults to 'all'):
        self.columns = columns

        # These are the only columns we are going to allow to be updated:
        # Although the API documentation shows 'name' as being mutable in their example, it actually isn't in our test rig.
        self.mutable_columns = []

        # We renamed some of the columnsto avoid reserved PG keywords (specifically "type").
        # While we were at it we went ahead and made some of the column names more verbose.
        # We do not flatten the config and state columns because they are different for each type of sensor.
        self.columnKeyMap = { 'sensor_type'      : 'type',
                              'sensor_name'      : 'name',
                              'manufacturer'     : 'manufacturername',
                              'model_id'         : 'modelid',
                              'software_version' : 'swversion',
                              'unique_id'        : 'uniqueid',
                              'config'           : 'config',
                              'state'            : 'state' }


    ############
    # We need to overload this function so Updates will work
    @property
    def rowid_column(self):
        return self._row_id_column


    ############
    # SQL SELECT:
    # We get back all of the lights we can find and roll them up into rows
    def execute(self, quals, columns):

        log_to_postgres('Hue Sensors Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Hue Sensors Query Filters:  %s' % quals, DEBUG)

        results = requests.get(self.baseURL)

        try:
            hueResults = json.loads(results.text)
        except:
            log_to_postgres('URL -- %s' % self.baseURL, DEBUG)
            log_to_postgres('Hue Sensors Query Request Results:  %s' % results.text, ERROR)


        for sensor in hueResults.keys():

            row = OrderedDict()

            ## add the requested columns to the output:
            for column in columns:

                # Not all sensors have these two values:
                if column == 'software_version' and not hueResults[sensor].has_key(self.columnKeyMap[column]):
                    row[column] = None
                    continue
 
                if column == 'unique_id' and not hueResults[sensor].has_key(self.columnKeyMap[column]):
                    row[column] = None
                    continue
 
                if column == 'sensor_id':
                    row['sensor_id'] = int(sensor)
        
                elif column in ['config', 'state']:
                    # HSTORE Column Type:
                    if self.kvType == 'hstore':
                        row[column] = hueResults[sensor][self.columnKeyMap[column]]
                    # JSON Column Type:
                    else:  
                        row[column] = json.dumps(hueResults[sensor][self.columnKeyMap[column]])
            
                else:
                    row[column] = hueResults[sensor][self.columnKeyMap[column]]

            ## decide if this is a row we should return or not:

            # Unfortunately the Hue API doesn't have much in the way of filtering when you get the data.
            # So we do it here.
            # There aren't really going to be all that many rows that we'll be throwing away so we should be ok.
            # This probably doesn't work with the json data types.  Need to ponder a solution...
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



    ############
    # SQL UPDATE:
    ## -- we should consider implementing 'rollback' (and, necessarily, 'commit')
    def update(self, sensorID, newValues):

        log_to_postgres('Hue Sensors Update Request - sensor_id:  %s' % sensorID, DEBUG)
        log_to_postgres('Hue Sensors Update Request - new values:  %s' % newValues, DEBUG)

        newState = {}
        for changedColumn in newValues.keys():

            # We are only going to be able to change the "state" columns.
            if changedColumn in self.mutable_columns:

                # 't' and 'f' are only going to show up on the boolean columns
                # We don't have any mutable boolean columns in the Sensors endpoint yet.
                if newValues[changedColumn] == 't':
                    newState[self.columnKeyMap[changedColumn]] = True
                elif newValues[changedColumn] == 'f':  
                    newState[self.columnKeyMap[changedColumn]] = False
                else:
                    newState[self.columnKeyMap[changedColumn]] = newValues[changedColumn]

        log_to_postgres(self.baseURL + '%s -- ' % sensorID + json.dumps(newState), DEBUG)

        results = requests.put(self.baseURL + '%s' % sensorID, json.dumps(newState))
        
        try:

            hueResults = json.loads(results.text)

        except Exception, e:

            log_to_postgres('Unexpected (non-JSON) response from the Hue Bridge: %s' % self.bridge, ERROR)
            log_to_postgres('%s' % e, ERROR)
            log_to_postgres('%s' % results, ERROR)
    

        for status in hueResults:

              if not status.has_key('success'):

                    log_to_postgres('Hue Sensors Full Results: %s' % results.text, DEBUG)
                    log_to_postgres('Hue Sensors Column Update Failed.', ERROR)
            

    ############
    # SQL INSERT:
    def insert(self, new_values):

        log_to_postgres('Hue Sensors Insert Request Not Yet Implemented - requested values:  %s' % new_values, WARNING)


    ############
    # SQL DELETE
    # There really is nothing
    def delete(self, old_values):

        log_to_postgres('Hue Sensors Delete Request Not Yet Supported by Hue Bridge - old values:  %s' % old_values, WARNING)



