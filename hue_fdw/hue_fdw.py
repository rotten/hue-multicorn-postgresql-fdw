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

        self.columns = columns


    # SQL SELECT:
    # We get back all of the lights we can find and roll them up into rows
    def execute(self, quals, columns):

        log_to_postgres('Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Query Filters:  %s' % quals, DEBUG)

        # Question:  Is this really capped at 15 results per GET, or will it return everything?
        # ie, do we need to loop this until we exhaust all of the lights in the system, or is one GET enough?
        hueResults = requests.getbase(baseURL + "/lights/")

        for light in hueResults.keys():

            # Unfortunately the Hue API doesn't have much in the way of filtering when you get the data.
            goodRow = True
            for qual in quals:

                try:

                    operatorFunction = getOperatorFunction(qual.operator)

                except unknownOperatorException, e:

                    log_to_postgres(e, ERROR)

                if not operatorFunction(light[qual.field_name], qual.value)):

                    # this column  didn't match.  Drop out and then move to the next row
                    goodRow = False
                    break

             if not goodRow:

                 # skip this row and try the next one
                 continue

             
             # By default, Multicorn seralizes dictionary types into something for hstore column types.
             # That looks something like this:   "key => value"
             # What we really want is this:  "{key:value}"
             # so we serialize it here.  (This is git issue #1 for this repo, and issue #86 in the Multicorn repo.)
             row = OrderedDict()
             for resultColumn in light.keys():

                 if type(resultRow[resultColumn]) is dict:

                     row[resultColumn] = json.dumps(resultRow[resultColumn])

                 else:

                     row[resultColumn] = resultRow[resultColumn]

             yield row
 

    # SQL INSERT:
    def insert(self, new_values):

        log_to_postgres('Insert Request Ignored - requested values:  %s' % new_values, DEBUG)

        return False

    # SQL UPDATE:
    def update(self, old_values, new_values):

        log_to_postgres('Update Request - new values:  %s' % new_values, DEBUG)

        return 

    # SQL DELETE
    # There really is nothing
    def delete(self, old_values):

        log_to_postgres('Delete Request Ignored - old values:  %s' % old_values, DEBUG)

        return False

