import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import rcParams


#%pylab inline
statsFile ="/Users/simonray/DropboxUiO/dropData/text_mining/entrez_searches/Blue_eye_stats.tsv"
dfStats=pd.read_csv(statsFile)

dfCountryData = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/countries.tsv", sep="\t")
dfStats["region"] = " "

def getRegionFromCountry(qCountry):
    print(qCountry)

    for indexC, countryEntry in dfCountryData.iterrows():
        if not qCountry:
            return ""
        for country in countryEntry['country'].split("|"):
            if country in qCountry:
                return countryEntry['region']
    return ""


for indexS, stat in dfStats.iterrows():
    if indexS > 62:
        print("pause")
    if pd.isna(stat['firstCountry']):
        dfStats.at[indexS, "region"] = "unknown"
        #stat["region"] = "unknown"
        print(str(indexS) + ":unknown -->" + ":unknown")
    else:
        dfStats.at[indexS, "region"] = getRegionFromCountry(stat['firstCountry'])
        print(str(indexS) + ":" + stat['firstCountry'] + " -->" + stat["region"])


#dfStats['impactFactor'].hist(bins=[1,2,3,4,5,6,7,8,9,10])
dfStatsAsia = dfStats[dfStats['region'] == 'Asia ']
rcParams.update({'figure.autolayout': True})
#sns.violinplot(x='impactFactor', data=dfStatsAsia,fontsize=12, linewidth=0.5)
sns.boxplot(x=dfStats['impactFactor'], y=dfStats['region'], palette="Blues")
print(dfStatsAsia['impactFactor'])
plt.xticks(fontsize=12)
plt.xlabel("impact factor", labelpad=14, fontsize=15)
plt.ylabel("region", labelpad=14, fontsize=15)

plt.savefig('/Users/simonray/DropboxUiO/dropData/text_mining/plots/blue_eye_IF_by_region_and_lastAuthor.TIFF',dpi=600, bbox_inches='tight')
plt.show()
