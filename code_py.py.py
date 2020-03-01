# -*- coding: utf-8 -*-
import pandas as pd
import janitor
import numpy as np
import matplotlib.pyplot as plt

df=pd.read_csv('ks-projects-201801.csv',encoding = "ISO-8859-1")
df.rename(columns={'usd pledged':'usd_pledged'},inplace=True)

#%%
#look for NaN
print(df.isna().sum())
#I suggest dropping the projects that do not have a name tag.
df = df.dropna(subset=['name'])
print(df.isna().sum())

'''
usd_pledged: conversion in US dollars of the pledged column (conversion done by kickstarter).
usd pledge real: conversion in US dollars of the pledged column (conversion from Fixer.io API).
usd goal real: conversion in US dollars of the goal column (conversion from Fixer.io API).

In 3797 cases Kickstarter did not convert the currency successfully to USD (usd_pledged) Let us further investigate that issue.
'''
#df where currency is USD, and USD_pledged differs from pledged even though the currency did not change
df[df['currency']=='USD'][['usd_pledged_real','usd_pledged','pledged','currency']][df['usd_pledged']!=df['pledged']].head(10)
#46581 entries seem to have a conversion error from USD to USD
#so how many others are there? How do other currencies look? Is Fixer.io good?

print(df.currency.unique())

#Google 28.02.2020
to_usd={'GBP':1.29, 'USD':1, 'CAD':0.74, 'AUD':0.65, 'NOK':0.11, 'EUR':1.1, 'MXN':0.05, 'SEK':0.10, 'NZD':0.63,'CHF':1.04, 'DKK':0.15, 'HKD':0.13, 'SGD':0.72, 'JPY':0.0092}

#function to compare what Kickstarter sais he currency is vs what it should be with current exchange rate within in margin X%
# inf values from deviding by 0 were marked with NaN and then replaced with the mean ignoring the NaNs
def within_Xp(df,X,to_usd=to_usd,col_base='pledged',col_comp='usd_pledged'):
    diff=df[col_base]*[to_usd[i] for i in df['currency']]/df[col_comp]
    diff.replace([np.inf, -np.inf], np.nan,inplace=True)
    diff.replace([np.nan], diff.mean(skipna=True),inplace=True)
    stats=[diff.mean(),diff.std(),len(diff[(diff>(1+X)) | (diff<(1-X))]),len(diff[(diff>(1+X)) | (diff<(1-X))])/len(df)]
    print(col_base,'vs',col_comp,'\nmean,std,,#out of dataset outside','1+-'+str(X),'%out of dataset outside','1+-'+str(X),'\n',stats)
    return diff[(diff>(1+X)) | (diff<(1-X))],stats


#Kickstarter conversion pledged to USD allowing a possible 30% change in currency since 2014
diff,stats=within_Xp(df,0.3,to_usd=to_usd,col_base='pledged',col_comp='usd_pledged')
diff.hist(bins=[0,1,2,3,4,5,6,7,8,9,10,20,50])
# the big spike is the inf entries changed to the mean
# 30% of the data is not within boundaries
print(diff.head(n=100))
#Fixer.io conversion pledged to USD allowing a possible 30% change in currency since 2014
diff,stats=within_Xp(df,0.3,to_usd=to_usd,col_base='pledged',col_comp='usd_pledged_real')
diff.hist(bins=50)
# at 40% there is no more outliers, so I believe it is best to drop pledged_usd and go with pledged_usd_real

df.drop(columns='usd_pledged',inplace=True)

#check for duplicates
df.duplicated().any()

#set datetime
df['launched']=pd.to_datetime(df['launched'])
df['deadline']=pd.to_datetime(df['deadline'])

#the categorical features and the contribution of the top 15 features to the data
for i in df.columns:
    print('\n',i,df[i].dtype)
    if df[i].dtype=='object' and i!='name':
        #print('# of categories in',i,len(df[i].unique()),'\n',df[i].unique())
        p={e:(df[i]==e).sum()/len(df) for e in df[i].unique()}
        p_sorted={k: v for k, v in sorted(p.items(), key=lambda item: item[1],reverse=True)}
        print({x:p_sorted[x] for c,x in enumerate(p_sorted) if c<15 },'\n')

test = df[df['ID'] == '1009317190']

print('Empty??', test.isna().sum())

####################
sum1 = df[['backers', 'usd_pledged_real', 'usd_goal_real']]
summary1 = {}
for columns in sum1.columns:
    summary1.update({columns : pd.Series([df[columns].count() - len(df.index), df[columns].mean(), df[columns].median(),
    df[columns].std(), df[columns].min(), df[columns].max(), df[columns].mode()])})
summary1 = pd.DataFrame(summary1)
print(summary1)

df.to_csv('C:/Users/vinde/OneDrive/Dokumenter/DTU/02450/Projects/Project_1/for_R.txt', sep = '\t')
#sum2 = df[['category', 'main_category', 'state', 'country']]
#summary2 = {}
#for columns in sum1.columns:
#    summary2.update({columns : pd.Series([df[columns].count() - len(df.index), df[columns].mean(), df[columns].median(),
#    df[columns].std(), df[columns].min(), df[columns].max(), df[columns].mode()])})
#summary2 = pd.DataFrame(summary2)
#print(summary2)
