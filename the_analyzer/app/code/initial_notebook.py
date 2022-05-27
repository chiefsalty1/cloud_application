#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Instructions:
#Sign up to kaggle
#go to accounts page and download kaggle api(.jason file)
#import kaggle to Anaconda
#.\pip install kaggle =>go to Anaconda folder and find pip.exe
#comment rest.py line 234,235(as anaconda python3 is not supported)
#path : C:\Program Files (x86)\Microsoft Visual Studio\Shared\Anaconda3_64\Lib\site-packages\kaggle\rest.py
#If college network : Allow kaggle.com to sign in manually and run the notebook.


# In[3]:


from kaggle.api.kaggle_api_extended import KaggleApi

import pandas as pd
import numpy as np
from zipfile import ZipFile
import io
import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')

username = "subbu1996"
key = "93ce57d81daccf52a7c36d217394d727"
api = KaggleApi({"username":username,"key":key})
api.authenticate()
#https://www.kaggle.com/martj42/international-football-results-from-18 72-to-2017
#owner_slug is the creator of that dataset. Its not the actual name of the creator. Its the username.
#dataset_slug is the dataset created by that perticular used above in owner_slug
owner_slug = "borismarjanovic"
dataset_slug = "price-volume-data-for-all-us-stocks-etfs"
file = api.datasets_download(owner_slug = owner_slug,dataset_slug = dataset_slug)
#file_withname = api.datasets_download_file(owner_slug = "martj42",dataset_slug = "international-football-results-from-1872-to-2017",file_name = "results.csv")
i = 0
with ZipFile(io.BytesIO(file)) as thezip:
    for zipinfo in thezip.infolist():        
        with thezip.open(zipinfo) as thefile:
            print(thefile)
            df = pd.read_csv(thefile, encoding='ISO-8859-1')
            if i == 10:
              break
            print(df.head(10), flush=true)
            i = i + 1


# In[ ]:




