import  numpy as np
import scipy.stats as si
from matplotlib import pyplot as plt
import pdb


def euro_call(S, K, T, r, sigma):
    #S: spot price
    #K: strike price
    #T: time to maturity
    #r: interest rate
    #sigma: volatility of underlying asset
    S = float(S)
    K = float(K)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    call = (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    return call


def euro_put(S, K, T, r, sigma):
    #S: spot price
    #K: strike price
    #T: time to maturity
    #r: interest rate
    #sigma: volatility of underlying asset
    S = float(S)
    K = float(K)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    put = (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))
    return put 

# diff % from strike 0.00-1.00 ( 0 to 100% )
def volSmile ( sigma, diff ) :
  diff = diff - 1.0 
  if  diff < 0:
     diff =  -diff
  assert (diff < 1)
  # 10% jump for 10% diff 
  return  ( sigma* ( 1 + ( 10  * (diff**2 ) ) ) )

#Reference --> https://www.quantconnect.com/tutorials/introduction-to-options/stochastic-processes-and-monte-carlo-method


###### Params ###########

iv = sigma0 = 0.18/np.sqrt(365*24*60) # per min  vol
sigmaNifty = 0.16/np.sqrt(365*24*60)
mu = 0.10 /(365*24*60) #  mean minute return TODO
r = 0.07/ ( 365*24*60 ) # per minute return


timetoEOD = 195 


##########################

start = 11600.0
dt = 1  # 1 minute simulation
steps = int ( timetoEOD - 6 )
e = np.exp(1)
numSimulations = 500 
min = max = start
profits = []
# 5 days of the week
timeToExp = [ 6*60*24 + timetoEOD,  3*60*24 + timetoEOD,  2*60*24 + timetoEOD, 1*60*24 + timetoEOD,  0*60*24 + timetoEOD ]
timeToExp = [  3*60*24 + timetoEOD ]
minv = 100
maxv = -100  
profile = { "both": [ ], "call": [] , "put":[] , "none" : [] }
c2c = 0 
incVolSmile = 0 
convertToStrangle = 1 
win_streak = 0
lose_streak = 0
max_ws = 0
max_ws_profit = 0
max_ls = 0
max_ls_loss = 0
for num_ in range( numSimulations ):
   np.random.seed( np.random.randint( 10000, 100000 ) )
   s = start + np.random.uniform(0,50)
   strike = start
   if ( s > start+25 ):
       strike = start +50 
   sigma = sigma0
   timeToExpirey = timeToExp [ num_ % len(timeToExp) ]
   calli = euro_call( s , strike, timeToExpirey  , r, sigma) 
   puti = euro_put ( s, strike, timeToExpirey, r, sigma)
   c_sl = calli * 1.5
   p_sl = puti * 1.5
   profit = 0
   slHit = 10**10
   meanvol = sigma0
   for i in range( steps ):
      s1 = s * e**( (mu - 0.5 * sigmaNifty**2 )*dt +  sigmaNifty*np.sqrt(dt)*np.random.normal(0, 1) )
      sigma = np.sqrt( 0.04*(meanvol**2)  + 0.04 * ( np.log(s1/s )**2 ) + 0.92*(sigma**2) ) 
      # vol Smile additiom
      if incVolSmile:
         sigmaO = volSmile ( sigma,(s1/start) ) 
      else:
         sigmaO = sigma
      
      s  = s1
      if c_sl != slHit:
         call_dt = euro_call( s , strike, timeToExpirey - i  , r, sigmaO )
      if p_sl != slHit:
         put_dt = euro_put ( s, strike, timeToExpirey-i, r, sigmaO )
      
      if (call_dt > c_sl and c_sl != slHit  ):
             profit = profit + calli - call_dt
             c_sl = slHit
             # Cost2Cost on the other leg
             if p_sl != slHit and c2c :
                p_sl = puti + calli - c_sl

      if ( put_dt >  p_sl and p_sl != slHit ):
             profit = profit + puti - put_dt
             p_sl = slHit   
             # Cost2Cost on the other leg
             if c_sl != slHit and c2c:
                c_sl = calli + puti - p_sl

      if ( p_sl == slHit and c_sl ==slHit ):
         break

   if ( p_sl != slHit ):
       profit = profit + puti - put_dt
   if ( c_sl != slHit ):
       profit = profit + calli - call_dt

   profits.append( profit*75 )
   if profit > 0:
       win_streak +=1
       lose_streak = 0
       if win_streak > max_ws:
          max_ws = win_streak
          max_ws_profit +=  profit*75
   else:
       lose_streak += 1
       win_streak = 0
       if lose_streak > max_ls:
          max_ls = lose_streak
          max_ls_loss += profit*75
        

   if ( p_sl != slHit and c_sl != slHit ):
         profile["none"].append(profit*75)
   elif ( p_sl ==slHit and c_sl == slHit ):
         profile["both"].append(profit*75)    
   elif ( p_sl == slHit ):
         profile["put" ].append(profit*75)
   else:
        profile["call"].append(profit*75)

for key in profile:
   profile[key].sort()

profits.sort()
arr = np.array( profits )       
print ( " Total Wins %d & loss %d,  Win%% %f " % ( len( arr[arr>0] ) , len(arr[arr<0] ),  len( arr[arr>0] )*100.0/len(arr) ) )
print ( " Total Profit = %d , average Profit per lot = %f " % ( sum( arr ), arr.mean() ) ) 
print( " average profit on win = %f , median profit on win = %f " % ( arr[ arr>0].mean(), np.median( arr [arr>0] ) ) )
print( " average loss on losing days = %f , median loss = %d " % ( arr[ arr<0].mean(), np.median( arr [arr<0] ) ) ) 
print ( " max_win_streak %d -> max winning steak profit %d " % ( max_ws, max_ws_profit ) ) 
print ( " max_lose_streak  %d -> max losing steak loss %d " % ( max_ls, max_ls_loss ) ) 
pdb.set_trace()      
       

