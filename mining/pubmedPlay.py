import pandas as pd
import numpy as np
from time import strftime, localtime

dfPubmed = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/covid_pubmed_data/citation_data/uniq_cites_cleaned_2.tsv", sep="\t")

print("loaded <" + str(len(dfPubmed)) + "> rows")
dfPubmed.groupby(['pubYear','pubMonth'])['numComments'].count().sort_values()
print("")
pubCount = dfPubmed.groupby(['pubYear','pubMonth'])['doi'].count()
df = pubCount.to_frame()
df.to_csv("/Users/simonray/DropboxUiO/dropData/text_mining/mining/uniq_cites_count_by_month.tsv")


