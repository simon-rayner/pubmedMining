
import pandas as pd
import re

dfPubmed = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/covid_pubmed_data/citation_data/uniq_cites2_cleansorted.tsv", sep="\t")
pmidsReddit = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/mining/PMIDsInReddit", sep="\t")



