## This is the implementation of the Multicorn ForeignDataWrapper class as an interface to the Philips Hue lighting system
## R.Otten - 2015

from collections import OrderedDict
import json

from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG

import requests

from operatorFunctions import unknownOperatorException, getOperatorFunction


## The Foreign Data Wrapper Class:
class HueFDW(ForeignDataWrapper):

    """
    Philips Hue Foreign Data Wrapper for PostgreSQL
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

        # We don't really use this anywhere.  Including it for now in case it ends up having a use.
        if options.has_key('hueid'):
            self.hueID = options['hueid']
        else:
            self.hueID = None
            log_to_postgres('hueID not set', DEBUG)

        self.columns = columns


    # SQL SELECT:
    def execute(self, quals, columns):

        log_to_postgres('Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Query Filters:  %s' % quals, DEBUG)

        for qual in quals:

            try:
                operatorFunction = getOperatorFunction(qual.operator)
            except unknownOperatorException, e:
                log_to_postgres(e, ERROR)

            myQuery = myQuery.filter(operatorFunction(r.row[qual.field_name], qual.value))

        hueResults = requests.get(---)
         
        # By default, Multicorn seralizes dictionary types into something for hstore column types.
        # That looks something like this:   "key => value"
        # What we really want is this:  "{key:value}"
        # so we serialize it here.  (This is git issue #1 for this repo, and issue #86 in the Multicorn repo.)

        for resultRow in hueResults:

            # I don't think we can mutate the row in the rethinkResults cursor directly.
            # It needs to be copied out of the cursor to be reliably mutable.
            row = OrderedDict()
            for resultColumn in resultRow.keys():

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
    def delete(self, old_values):

        log_to_postgres('Delete Request Ignored - old values:  %s' % old_values, DEBUG)

        return False

