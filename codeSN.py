# -*- coding: utf-8 -*-
import pandas as pd

a=pd.read_csv('ks-projects-201612.csv',encoding = "ISO-8859-1")
#remove empty columns
a_drop=[i for i in a.columns if 'Unnamed' in i]
a.drop(a_drop,axis=1,inplace=True)
b=pd.read_csv('ks-projects-201801.csv',encoding = "ISO-8859-1")
#%%
a