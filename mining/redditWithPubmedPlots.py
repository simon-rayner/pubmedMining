import pandas as pd


dfRedditByDateCopy = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/mining/redditPlusPubmed.tsv", sep="\t")

dfRedditByDateCopy['pubcat2'] = ""

dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'PUB','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'SPUB','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'PNAS','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'JAMA','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'NEJM','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'NATURE','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'BMJ','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'CDC','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'LANCET','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']=='PPP','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'CELL','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'NEJ','pubcat2'] = 'ResearchPublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'SCIENCE','pubcat2'] = 'ResearchPublished'

dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'PP','pubcat2'] = 'ResearchUnpublished'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']=='PPU','pubcat2'] = 'ResearchUnpublished'

dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'RETRACTED','pubcat2'] = 'ResearchRetracted'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'NRETRACTED','pubcat2'] = 'ResearchRetracted'

dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'Missing','pubcat2'] = 'NoInformation'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'LBLOG','pubcat2'] = 'LancetBlog'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'SBLOG','pubcat2'] = 'ScienceBlog'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'BLOG','pubcat2'] = 'BLOG'

dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'NEWS','pubcat2'] = 'OtherNews'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'NNEWS','pubcat2'] = 'NatureNews'
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']== 'SNEWS','pubcat2'] = 'ScienceNews'

dfRedditByDateCopy.to_csv("/Users/simonray/DropboxUiO/dropData/text_mining/mining/redditPlusPubmedExtraCats.tsv", sep="\t")



import seaborn as sns
import matplotlib.pyplot as plt
from time import strftime, localtime
#fig, ax = plt.subplots(1, figsize=(12,10))
#sns.pairplot(dfRedditByDateCopy, vars=['numComments', 'citationCount'],  hue='pubcat2', plot_kws=dict(s=80, edgecolor="blue", linewidth=2.5, alpha=0.3))

fig, ax = plt.subplots(1, figsize=(12,10))
sns.scatterplot(x='numComments', y='citationCount', data=dfRedditByDateCopy, hue='pubcat2', alpha=0.6)
plt.ylim(0, 100)
plt.show()

fig, ax = plt.subplots(1, figsize=(12,10))
sns.stripplot(y="pubcat2", x="citationCount", data=dfRedditByDateCopy)

dfRedditByDateCopy['date'] = pd.to_datetime(dfRedditByDateCopy['created_utc'], unit='s').dt.to_period('M')

