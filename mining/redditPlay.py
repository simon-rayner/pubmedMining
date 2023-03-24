import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import numpy as np
from time import strftime, localtime


dfReddit = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/reddit/submission_dumps/reddit_top1945_commented_submissions_on_manuscript_w_dois_classes__BiorMedrDOIs.tsv", sep="\t")

print("loaded <" + str(len(dfReddit)) + "> rows")
print("")
#strftime('%Y-%m-%d %H:%M:%S', localtime(1347517370))
dfRedditByDate=dfReddit[dfReddit['created_utc']!='missing']
#dfRedditByDate['postmonth'] = dfRedditByDate.apply(localtime, dfRedditByDate['retrieved_on'].astype('int'))
#dfRedditByDate['postmonth'] = 0
#dfRedditByDate
#ocaltime(int(dfRedditByDate.iloc[1]['retrieved_on']))
print("after filtering, left with <" + str(len(dfRedditByDate)) + "> submissions")
dfRedditByDate.assign(postmonth=0)
for index, row in dfRedditByDate.iterrows():
    val = strftime('%Y-%m', localtime(int(row['created_utc'])))
    dfRedditByDate.loc[index, 'postmonth'] = val

print("done")

dfRedditByDate.groupby('postmonth')['numComments'].count().sort_values()
print("done")
