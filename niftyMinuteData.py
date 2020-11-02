# Copyright (c) 2020 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from __future__ import absolute_import, division, print_function
import argparse
import datetime
import urllib2
import simplejson
import numpy as np
import math

def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

my_parser = argparse.ArgumentParser()
my_parser.add_argument('-d',
      '--date',
      action='store',
      help="The Start Date - format YYYY-MM-DD", 
      required=True, 
      type=valid_date)

args = my_parser.parse_args()
import pdb
start = args.date - datetime.timedelta(hours=4, minutes=15)
end = args.date + datetime.timedelta( hours=2)
link = "https://priceapi.moneycontrol.com/techCharts/history?symbol=9&resolution=1&from=%s&to=%s" % (start.strftime("%s"), end.strftime("%s"))
req = urllib2.Request(link)
resp = urllib2.urlopen(req)
data = resp.read()
data =  simplejson.loads(data)
if data['s'] == 'ok':
   returns = [ np.log(data['c'][i+1]*1.0/ data['c'][i])  for i in xrange(len(data['c']) - 1 )]  
   #returns = returns[-195:]
   stdDev = np.std( returns )*math.sqrt(365*60*24)
   print( "daily stdDev on %s is %f%%" % ( args.date.strftime("%Y-%m-%d"), stdDev*100 ))

