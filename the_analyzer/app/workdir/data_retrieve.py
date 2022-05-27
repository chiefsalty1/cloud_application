'''
'  Author: Subash Sunku
'  Description:  Simple script to download stock data from Kaggle, distribute the work to a cluster of docker nodes,
'  calculate stock data prior H1N1 pandemic, and data prior Covid Pandemic and see if there is a trend to predict a furture pandemic decline.
'
'  Change Log:
'  2020-04-27   AGG  Added file header and description
'  2020-04-27   AGG  Added download funtion with temporary content limiter to work on a small subset.  Set limit to 0 for it to be ignored.
'  2020-04-27   AGG  Narrowed column data to Date, Close and Adj Close of the downloaded data. Added filter dates.
'  2020-04-27   AGG  Separated logic to prevent the utf8 exception from killing the for loop.
'  2020-05-01   SS   Download datasets using work nodes and send back to master node into a single DF - date range : 1st Jan 2009 to 1st Aug 2010.
'''
from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
import numpy as np
from zipfile import ZipFile
import io
#from time import process_time as ps
import matplotlib.pyplot as plt
from matplotlib import style
import datetime
from mpi4py import MPI
import math
import sys

#replace with your own credentials. Can be found in kaggle.json downloaded from Account page of kaggle.com
username = "subbu1996"
key = "c6105db7bbad4ffb468b6d2d3a1820a2"
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
api = KaggleApi({"username":username,"key":key})
api.authenticate()
owner_slug = "borismarjanovic"
dataset_slug = "price-volume-data-for-all-us-stocks-etfs"
#start = ps()


#AGG 2020-04-27 show columns
pd.set_option('display.max_columns', 8)
pd.set_option('display.width', 1000)

#AGG 2020-04-27 Filter dates ( from UI perspective should come from CLI
H1N1_dtf = "04/01/2009"
H1N1_dto = "04/30/2010"
COVID_dtf = "12/31/2019"
COVID_dto = "04/30/2020"

#AGG 2020-04-27 Filter containers
local_h1n1_df = None
local_covid_df = None

#SLS 2020-05-03 Variable for filling NaN entries
fill_nan = -999

def display_files():
    #files = api.dataset_list_files_cli('borismarjanovic/price-volume-data-for-all-us-stocks-etfs')
    #print(files)
    #files_present = api.datasets_list_files('jacksoncrow','stock-market-dataset')
    #files = [];
    #file1 = open("myfile.txt","w")
    #file1.write(files_present)
    #print(files_present['datasetFiles'])
    #for li in files_present['datasetFiles']:
    #    files.append(li['ref'])
    file_ = api.datasets_download_file('jacksoncrow','stock-market-dataset','symbols_valid_meta.csv')
    df=pd.read_csv(io.StringIO(file_.decode('utf-8')))
    files = df['NASDAQ Symbol'].tolist() # Matches to file names
    return files
        #for ref, creationDate, datasetRef, description, fileType, name, ownerRef, totalBytes, url, columns in li:
            #print(ref)
        #file = api.datasets_download_file('jacksoncrow','stock-market-dataset',li['ref'])
        #try:
        #        c=pd.read_csv(io.StringIO(file.decode('utf-8')))
        #        print(c.head(2))
        #except:
        #        print('Error in file',li['ref'])
        #        pass
#print(ps() - start)

#AGG 2020-04-27 moved reading into separate method.  Some files break on utf-8 decode and kills for loop
#pass or continue not working like in other languages.
#method returns a dataframe or None or error
def read_file(f):
    ret_val = None
    try:
      #Focus on Date, Close Adj. Close from file
      c=pd.read_csv(io.StringIO(f))
      ret_val = c[['Date','Close','Adj Close']]

    except:
        print(sys.exc_info()[0])
        ret_val = None

    return ret_val

def create_labels(cur_rate, prev_rate):
    '''This function returns a label based on the change criteria. If the
    current value is Not a Number, then NoData is returned. If the difference
    is positive, then Up is returned. If the difference is negative, then
    Down is returned. The default returns None, since the two values are
    assumed to be equal.'''
    if cur_rate == fill_nan or cur_rate == np.nan:
        return 'NoData'
    elif cur_rate > prev_rate:
        return 'Up' # rate goes up
    elif cur_rate < prev_rate:
        return 'Down' # rate goes down
    else:
        return 'None' # rate has not changed

#AGG 2020-04-27 moving download into separate routine
#limit is a test param to limit download to work on a small subset
def download_files_alex(d_files, rk, limit = 0):
    i = 0
    for d in d_files:
        if (  limit > 0 and i == limit ):
          break

        i += 1
        file = api.datasets_download_file('jacksoncrow','stock-market-dataset',d)
        nf = read_file(file)

        if ( not nf.empty ):
            print(nf)
            #TODO: Filter
def download_files(d_files,r):
#   start_date = '01-01-2009'
#    end_date = '08-01-2010'
    final = pd.DataFrame()
    for d in d_files:
        d = 'stocks/'+d+'.csv'
        try:
            file_ = api.datasets_download_file('jacksoncrow','stock-market-dataset',d,dataset_version_number = 2)
        except Exception as e:
            print('Rank: ',r,'File not found - ',d)
            #print('Rank: ',r,'Exception: ',e)
        try:
                #file = api.datasets_download_file('jacksoncrow','stock-market-dataset',d)
                df = pd.read_csv(io.StringIO(file_.decode('utf-8')))
                df.drop(columns = ['Open','High','Low','Close','Volume'],inplace = True)
                df['Date'] = pd.to_datetime(df['Date'])
#                mask = (df['Date'] > start_date) & (df['Date'] <= end_date)
#                df = df.loc[mask]
                df.rename(columns={"Adj Close":d},inplace = True)
                #df2 = df.transpose()
                #new_header = df2.iloc[0]
                #df2 = df2[1:]
                #df2.columns = new_header
                df.set_index('Date', inplace=True)
                final = pd.concat([final,df],axis = 1)
                #print("rank: ",r,"file name: ",d,'shape: ',df.shape)
                #print(df.head(1))
                #print("max date: ",max(df['Date']),"min date",min(df["Date"]))
        except Exception as e:
                print('Rank: ',r,' - exception: ',e)
                #print('Error in file',d)
                pass
#    final.dropna(axis = 'columns',inplace = True,how = 'all')
#    final = final.pct_change()
    return final

def labels( symbols, hold_df ):
    hold_change_df = pd.DataFrame()
    for symbol in symbols:
        hold_change_df[symbol] = list(map(create_labels,hold_df[symbol],hold_df[symbol].shift(1))) # Create labels for positive, negative or zero change
    return hold_change_df.apply(pd.Series.value_counts, axis=1)

def percent_changed( changed_stocks ):
    hold_change = pd.DataFrame()
    no_data = "NoData"
    count = len(changed_stocks)
    for col in changed_stocks.columns:
        hold_change[col] = changed_stocks.loc[:, (col)]/(count - changed_stocks.loc[:, (no_data)])

    return hold_change

start_date = '01-01-2009'
end_date = '08-01-2010'


if rank == 0:
        files = display_files()
        files_num = len(files)
        opti_num = math.floor(files_num/(size-1))
        reminder = files_num%(size-1)
        count = 0
        final_df = pd.DataFrame()
        #print("Rank ",rank,"length ",files_num)
        #print("Rank ",rank,"files:",files)
        for i in range(1, size):
            if reminder == 0:
                comm.send(files[opti_num*(i-1):opti_num*i],dest = i)
            else:
                comm.send(files[opti_num*(i-1) + count:opti_num*i + 1 + count],dest = i)
                reminder -= 1
                count += 1
            df = comm.recv(source = i)
            final_df = pd.concat([final_df,df],axis = 1)
        print(final_df.info)
else:
    hold_work = pd.DataFrame()
    hold_final = pd.DataFrame()
    changed_df = pd.DataFrame()
    
    data = comm.recv(source = 0)
    #print("Rank ",rank,"length ",len(data))
    #print("Rank ",rank,"files:",data)
    print("")

    #AGG 2020-04-27
    hold_work = download_files(data,rank)
    changed_df = labels(data, hold_work.fillna(fill_nan))
    pct_changed_df = percent_changed(changed_df.loc[:, ('None', 'Down', 'Up')])
    final = hold_work.pct.change()
    comm.send(final,dest = 0)

