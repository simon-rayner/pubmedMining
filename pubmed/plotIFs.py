# before 2019
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os.path
rootFolder = '/Users/simonray/DropboxUiO/dropData/text_mining/results/african_swine_fever/'
statsFile ="African_swine_stats.tsv"

#%pylab inline
statsFilePath = os.path.join(rootFolder, statsFile)
dfStats=pd.read_csv(statsFilePath)
gSplitYear = 2011

dfStatsBeforeSplit=dfStats[dfStats['year'] < gSplitYear]
outputFileBefore = statsFile.split(".")[0] + "_IFs_FirstAuthor_before_" + str(gSplitYear) + ".tiff"
outputFileBeforePath = os.path.join(rootFolder, outputFileBefore)
beforeTitle = "IFs by country before " + str(gSplitYear)

dfStatsAfterSplit=dfStats[dfStats['year'] >= gSplitYear]
outputFileAfter = statsFile.split(".")[0] + "_IFs_FirstAuthor_after_" + str(gSplitYear + 1) + ".tiff"
outputFileAfterPath = os.path.join(rootFolder, outputFileAfter)
afterTitle = "IFs by country before " + str(gSplitYear + 1)
print(outputFileBeforePath)


# Before
plt.figure(figsize=(6,18))
sbViolin=sns.violinplot(y='firstCountry', x='impactFactor',
               data=dfStatsBeforeSplit,fontsize=12, linewidth=0.5)
sbViolin.set_title(beforeTitle, fontsize=18, color='darkslategray')
plt.xlabel("impactFactor", labelpad=14, fontsize=14)
plt.ylabel("country", labelpad=14, fontsize=14)

plt.savefig(outputFileBeforePath,dpi=600, bbox_inches='tight')
plt.show()


sbBoxplot=sns.boxplot(x=dfStats['impactFactor'], y=dfStats[dfStats['firstCountry']!='unknown']['firstCountry'], palette="Blues")
sbBoxplot.set_title(beforeTitle, fontsize=18, color='darkslategray')

plt.xlabel("impact factor", labelpad=14, fontsize=15)
plt.ylabel("region", labelpad=14, fontsize=15)
plt.title("IF of published work by first author country ", fontsize=18)
plt.xlim([0, 25])
plt.savefig('/Users/simonray/DropboxUiO/dropData/text_mining/results/african_swine_fever/african_swine_fever_IF_by_region_and_lastAuthor_before2019.TIFF',dpi=600, bbox_inches='tight')
plt.show()


plt.xticks(fontsize=12)
#plt.title(beforeTitle, labelpad=14, fontsize=18)



#After
plt.figure(figsize=(6,18))
p=sns.violinplot(y='firstCountry', x='impactFactor', data=dfStatsAfterSplit,fontsize=12, linewidth=0.5)
p.set_title(afterTitle, fontsize=18, color='darkslategray')
plt.xticks(fontsize=12)
#plt.title(beforeTitle, labelpad=14, fontsize=18)
plt.xlabel("impactFactor", labelpad=14, fontsize=14)
plt.ylabel("country", labelpad=14, fontsize=14)

plt.savefig(outputFileAfterPath,dpi=600, bbox_inches='tight')
plt.show()


