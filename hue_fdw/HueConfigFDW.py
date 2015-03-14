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
## This file has the one for the * Config * endpoint in it.
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
## The Foreign Data Wrapper Class for Config:
##
## Options:
##  bridge   -- Required:  The IP address for the Hue Bridge
##  username -- Required:  The API user name - configured when the bridge is set up 
##              (see http://www.developers.meethue.com/documentation/getting-started )
##  hueid    -- Optional:  The Hue system ID - not used at this time
##  kvtype   -- Optional:  json or hstore - Whether nested KV data returns JSON format or HSTORE format. (default:  json)
##
class HueConfigFDW(ForeignDataWrapper):

    """
    Philips Hue Lights Foreign Data Wrapper for PostgreSQL
    """

    def __init__(self, options, columns):

        super(HueLightsFDW, self).__init__(options, columns)

        log_to_postgres('Hue Config options:  %s' % options, DEBUG)
        log_to_postgres('Hue Config columns:  %s' % columns, DEBUG)

        if options.has_key('bridge'):
            self.bridge = options['bridge']
        else:
            log_to_postgres('bridge IP address is required for Hue Config setup.', ERROR)

        if options.has_key('username'):
            self.userName = options['username']
        else:
            self.userName = 'postgreshue'
            log_to_postgres('Using Default Username for Hue Config setup:  postgreshue.', WARNING)

        self.baseURL = 'http://' + self.bridge + "/api/" + self.userName + "/config/"

        # We don't really use this anywhere.  Including it for now in case it ends up having a use.
        if options.has_key('hueid'):
            self.hueID = options['hueid']
        else:
            self.hueID = None
            log_to_postgres('hueID not set in Hue Config setup', DEBUG)

        # Give the user a choice as to whether they want to serialize Dictionaries into 
        # HSTORE or JSON.  By default Multicorn serializes them to HSTORE.  (Issue #86 in the Multicorn Repo.)
        if options.has_key('kvtype'):
            if options['kvtype'].lower() in ['hstore', 'json']:
                self.kvType = options['kvtype'].lower()
            else:
                log_to_postgres('Invalid Key Value Type for Hue Config setup: %s. (Choose "hstore" or "json")' % options['kvType'], ERROR)
        else:
            self.kvType = 'json'

        ###
        # We need to identify the "primary key" column so we can do updates:
        self._row_id_column = 'name'

        # The columns we'll be using (defaults to 'all'):
        self.columns = columns

        # These are the only columns we are going to allow to be updated though:
        self.mutable_columns = ['name', 
                                'proxyport', 
                                'proxyaddress', 
                                'swupdate', 
                                'linkbutton', 
                                'ipaddress', 
                                'netmask', 
                                'dhcp',
                                'timezone']

        # We did not rename any of the columns for the config endpoint
        #self.columnKeyMap = { }


    ############
    # We need to overload this function so Updates will work
    @property
    def rowid_column(self):
        return self._row_id_column


    ############
    # SQL SELECT:
    # We get back all of the lights we can find and roll them up into rows
    def execute(self, quals, columns):

        log_to_postgres('Hue Config Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Hue Config Query Filters:  %s' % quals, DEBUG)

        # Question:  Is this really capped at 15 results per GET, or will it return everything?
        # ie, do we need to loop this until we exhaust all of the lights in the system, or is one GET enough?
        results = requests.get(self.baseURL)

        hueResults = json.loads(results.text)
         
        row = OrderedDict()

        # add the requested columns to the output:
        for column in columns:

            if column in ['swupdate', 'portalstate']:
                # HSTORE Column Type:
                if self.kvType == 'hstore':
                    row[column] = hueResults[column]
                # JSON Column Type:
                else:  
                    row[column] = json.dumps(hueResults[column])

            elif column == 'proxyport':
                row[column] = int(hueResults[column])

            else:
                row[column] = hueResults[column]

        # we only ever get one row back.  We are going to ignore quals.
        if len(quals):
            log_to_postgres('Hue Config Select called with qualifiers - IGNORED', WARNING)

        yield row
 


    ############
    # SQL UPDATE:
    ## -- we should consider implementing 'rollback' (and, necessarily, 'commit')
    def update(self, name, newValues):

        log_to_postgres('Hue Config Update Request - name:  %s' % lightID, DEBUG)
        log_to_postgres('Hue Config Update Request - new values:  %s' % newValues, DEBUG)

        newState = {}
        for changedColumn in newValues.keys():

            # We are only going to be able to change the "state" columns.
            if changedColumn in self.mutable_columns:

                # 't' and 'f' are only going to show up on the boolean columns
                if newValues[changedColumn] == 't':
                    newState[changedColumn] = True
                elif newValues[changedColumn] == 'f':  
                    newState[changedColumn] = False
                else:
                    newState[changedColumn] = newValues[changedColumn]

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

                    log_to_postgres('Hue Config Full Results: %s' % results.text, DEBUG)
                    log_to_postgres('Hue Config Column Update Failed.', ERROR)
            

    ############
    # SQL INSERT:
    def insert(self, new_values):

        log_to_postgres('Hue Config Insert Request Ignored - requested values:  %s' % new_values, WARNING)


    ############
    # SQL DELETE
    # There really is nothing
    def delete(self, old_values):

        log_to_postgres('Hue Config Delete Request Ignored - old values:  %s' % old_values, WARNING)



