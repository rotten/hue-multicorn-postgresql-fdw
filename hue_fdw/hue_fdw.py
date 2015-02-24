## This is the implementation of the Multicorn ForeignDataWrapper class as an interface to the Philips Hue system
## R.Otten - 2015

from collections import OrderedDict
import json

from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG

import requests

from operatorFunctions import unknownOperatorException, getOperatorFunction


## The Foreign Data Wrapper Class for Lights:
class HueLightsFDW(ForeignDataWrapper):

    """
    Philips Hue Lights Foreign Data Wrapper for PostgreSQL
    """

    def __init__(self, options, columns):

        super(HueFDW, self).__init__(options, columns)

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
        if options.has_key('kvType')
            if options['kvType'].lower() in ['hstore', 'json']:
                self.kvType = options['kvType'].lower()
            else:
                log_to_postgres('Invalid Key Value Type: %s. (Choose "hstore" or "json")' % options['kvType'], ERROR)
        else:
            self.kvType = 'json'

        self.columns = columns


    ############
    # SQL SELECT:
    # We get back all of the lights we can find and roll them up into rows
    def execute(self, quals, columns):

        log_to_postgres('Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Query Filters:  %s' % quals, DEBUG)

        # Question:  Is this really capped at 15 results per GET, or will it return everything?
        # ie, do we need to loop this until we exhaust all of the lights in the system, or is one GET enough?
        hueResults = requests.getbase(baseURL + "/lights/")

  
        row = OrderedDict()
        for light in hueResults.keys():

            row['light_id']  = light
            row['swversion'] = hueResults[light]['swversion']
            row['uniqueid']  = hueResults[light]['uniqueid']
            row['type']      = hueResults[light]['type']
            row['modelid']   = hueResults[light]['modelid']

            # We are going to flatten out the "state" inner json.
            row['on']        = hueResults[light]['state']['on']
            row['hue']       = hueResults[light]['state']['hue']
            row['colormode'] = hueResults[light]['state']['colormode']
            row['effect']    = hueResults[light]['state']['effect']
            row['alert']     = hueResults[light]['state']['alert']
            row['xy']        = hueResults[light]['state']['xy']
            row['reachable'] = hueResults[light]['state']['reachable']
            row['bri']       = hueResults[light]['state']['bri']
            row['sat']       = hueResults[light]['state']['sat']
            row['ct']        = hueResults[light]['state']['ct']

            # Pointsymbol isn't used yet.  We'll save it as is.
            # HSTORE Column Type:
            if self.kvType = 'hstore':
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

                if not operatorFunction(row[qual.field_name], qual.value)):

                    # this column  didn't match.  Drop out and then move to the next row
                    goodRow = False
                    break

             if goodRow:

                 yield row
 
             # otherwise, loop around and try the next row


    ############
    # SQL UPDATE:
    def update(self, old_values, new_values):

        log_to_postgres('Update Request - new values:  %s' % new_values, DEBUG)

        return 

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

