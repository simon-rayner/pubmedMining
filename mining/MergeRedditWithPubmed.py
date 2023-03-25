import matplotlib.pyplot as plt
import pandas as pd
import re

def calculateTimeDifference(pubYear, pubMonth, createdUTC):
    from time import strftime, localtime
    redditMonth = strftime('%m', localtime(int(createdUTC)))
    redditYear = strftime('%Y', localtime(int(createdUTC)))

    difference = 0
    if int(pubYear) < int(redditYear):
        print("something weird happened")

    difference = 12*(int(pubYear) - int(redditYear)) + (int(pubMonth) - int(redditMonth))

    return difference


dfPubmed = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/covid_pubmed_data/citation_data/uniq_cites_cleaned_2.tsv", sep="\t")
dfRedditByDate = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/reddit/submission_dumps/reddit_top1945_commented_submissions_on_manuscript_w_dois_classes__BiorMedrDOIs.tsv", sep="\t")
dfRedditByDate['citationCount']=0
dfRedditByDate['pubMedYear']=0
dfRedditByDate['pubMedMonth']=0
dfRedditByDate['timeDifference']=-1
dfRedditByDate['journalISOAbbreviation'] = ""
dfRedditByDate['journalISSN'] = ""
dfRedditByDate['PMID'] = ""


#dfRedditByDate.assign(citationCount=0)

foundCount = 0
for index, row in dfRedditByDate.iterrows():
    print(str(row['i']) + ":\t" + row['url'])
    # get rid of preceding doi.org
    doiString = str(row['doi'])
    print("--" + str(doiString))
    if doiString == 'nan':
        print("--nan")
        doiString = 'none'
        print("--> none")

    if 'doi:' in doiString:
        doiString = re.sub(r'^.*?:', '', row['doi']).strip()
        print("--trimmed doi: from doi String")
        print("-->" + str(doiString))

    if 'doi.org' in doiString:
        doiString = re.sub(r'^.*?/', '', row['doi']).strip()
        print("--trimmed doi.org from doi String")
        print("-->" + str(doiString))

    if 'dx.doi.org' in doiString:
        doiString = re.sub(r'^.*?x', '', row['doi']).strip()
        doiString = re.sub(r'^.*?/', '', doiString).strip()

    if 'doi' in doiString:
        print("--got a weird one")

    hit = dfPubmed[dfPubmed['doi'].str.contains(re.escape(doiString), na=False)]
    if len(hit) == 0:
        print("--not found")

    if len(hit) == 1:
        print("--found")
        dfRedditByDate.loc[index, 'citationCount'] = int(hit.iloc[0]['citationCount'])
        dfRedditByDate.loc[index, 'pubMedYear'] = hit.iloc[0]['pubYear']
        dfRedditByDate.loc[index, 'pubMedMonth'] = hit.iloc[0]['pubMonth']
        dfRedditByDate.loc[index, 'timeDifference'] = calculateTimeDifference(hit.iloc[0]['pubYear'], hit.iloc[0]['pubMonth'], row['created_utc'])
        dfRedditByDate.loc[index, 'journalISOAbbreviation'] = hit.iloc[0]['journalISOAbbreviation']
        dfRedditByDate.loc[index, 'journalISSN'] = hit.iloc[0]['journalISSN']
        dfRedditByDate.loc[index, 'PMID'] = hit.iloc[0]['PMID']

        foundCount+=1

    if len(hit) > 1:
        print("--found multiple hits!")

    print("next")

# now i have a list of publications with citationCounts + comments. I want to write these out


dfRedditByDate.to_csv("/Users/simonray/DropboxUiO/dropData/text_mining/mining/redditPlusPubmed.tsv", sep="\t")

print(foundCount)
dfRedditByDateCopy = dfRedditByDate
dfRedditByDateCopy.loc[dfRedditByDateCopy['pub_category']=='PPP','pubcat2'] = 'ResearchPublication'

import seaborn as sns
import matplotlib.pyplot as plt
sns.pairplot(dfRedditByDate, vars=['numComments', 'citationCount'],  hue='pubcat2', plot_kws=dict(s=80, edgecolor="blue", linewidth=2.5, alpha=0.3))


sns.scatterplot(x='numComments', y='citationCount', data=dfRedditByDate, hue='pubcat2', alpha=0.6)
plt.ylim(0, 100)
plt.show()

fig, ax = plt.subplots(1, figsize=(12,10))
sns.scatterplot(y="pubcat2", x="numComments Score", data=dfRedditByDateCopy, marker='|', s=1000, color='k')
sns.stripplot(y="pubcat2", x="numComments", data=dfRedditByDateCopy)


