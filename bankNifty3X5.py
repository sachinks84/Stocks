from __future__ import absolute_import, division, print_function
import argparse
from  datetime import datetime
import urllib2
import json
import numpy as np
import pandas as pd
import math
import pdb

def emaN( N, stockPrice , emaOld ):
     return ( stockPrice*2.0/(N+1) + ( 1 - 2.0/(N+1) )* emaOld )

start = datetime.strptime( "2010-11-16","%Y-%m-%d")
end = datetime.strptime( "2020-11-16","%Y-%m-%d")
link = "https://priceapi.moneycontrol.com/techCharts/history?symbol=23&resolution=d&from=%s&to=%s" % (start.strftime("%s"), end.strftime("%s"))
req = urllib2.Request(link)
resp = urllib2.urlopen(req)
data = resp.read()
data =  json.loads(data)
oldema3 = oldema5 =   data['c'][ 0 ] 
ema3 = []
ema5 = []
# 0 --> no trade , 1 -> buy, -1 is sell
state = 0
tradePrice = 0
reversal = []
points = []
dates = []
transaction = []
intraDayExit = []
trade = []
trNo = 0 
for idx, close  in  enumerate( data['c'] ):
    profit = 0
    rev = 4*oldema5 - 3*oldema3
    reversal.append( rev )
    dates.append( datetime.fromtimestamp(data['t'][idx]).strftime("%Y-%m-%d") )
    # calculate the new Emas for closing price today
    oldema3 = emaN(3, close, oldema3 )
    oldema5 = emaN(5, close, oldema5 )
    ema3.append( '%.2f' % oldema3 )
    ema5.append( '%.2f' % oldema5 )
    exit = 1
    idExit = ''
    if state != 0 : 
       if state==1 : 
         # we were long
         idExit = 'Sell'
         if data['o'][idx] < rev:
            profit = data['o'][idx] - tradePrice
         elif data['l'][ idx ] <  rev:
            profit = rev  - tradePrice
         else:
            idExit = '-'
            exit = 0
       else:
          #we were short 
          idExit = 'Buy'
          if data['o'][idx] >  rev:
             profit =  tradePrice - data['o'][idx]
          elif data['h'][idx] > rev:
             profit =  tradePrice -rev   
          else:
             idExit = '-'
             exit = 0

       if exit == 1:
          # SL  got hit and we exited during the day
          state = 0  

    intraDayExit.append(idExit)

    if oldema3 > oldema5:
       # go long 
       if state == -1:
          assert( profit == 0)
          profit = tradePrice - close 
          state = 1
          transaction.append("Buy") 
          trNo += 1
          tradePrice = close
       elif state == 0:
          tradePrice = close
          state = 1
          trNo += 1
          transaction.append("Buy") 
       else:
          transaction.append("X") 
       trade.append( trNo )
    else: 
       # go short
       if state == 1: 
          assert( profit == 0)
          profit = close  - tradePrice   
          state = -1
          trNo += 1
          tradePrice = close
          transaction.append("Sell") 
       elif state ==0:
          tradePrice = close # sell
          state = -1
          trNo += 1
          transaction.append("Sell") 
       else:
          transaction.append("X") 
       trade.append( trNo )
           
    if profit != 0:
       points.append('%.2f'% profit)
    else:
       points.append(0)     
       
#points = np.array( points )    
colms = [ 'date', 'open', 'high', 'low', 'close', '3Ema', '5Ema','Reversal', 'transaction', 'IntraDayExit', 'tradeNo', 'profit' ]
df = pd.DataFrame( { 'date' : dates, 'open' : data['o'], 'high':data['h'], 'low' : data['l'], 'close': data['c'],
   '3Ema' : ema3, '5Ema' : ema5, 'Reversal' : reversal,
   'transaction': transaction, 'IntraDayExit' : intraDayExit,  'tradeNo' : trade, 'profit': points } )
with open( "bnf.csv", "w" ) as f:
     f.write(df.to_csv(index=False,columns=colms ))

