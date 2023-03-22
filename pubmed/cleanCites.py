import pandas as pd

dfPMCites=pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/covid_pubmed_data/citation_data/uniq_cites.tsv", sep='\t')

for index, row in dfPMCites.iterrows():
    if index%1000 == 0:
        print(str(index))
    try:
        if ',' in str(row['citationCount']):
            print()
            set = dfPMCites.iloc[index]['citationCount']
            dfPMCites.loc[index, 'citationSet'] = set
            dfPMCites.loc[index, 'citationCount'] = 0
            continue

        if len(str(row['citationCount']))>5:
            set = dfPMCites.iloc[index]['citationCount']
            dfPMCites.loc[index, 'citationSet'] = set
            dfPMCites.loc[index, 'citationCount'] = 0
            continue
    except:
        print(row['citationCount'])

dfPMCites.to_csv("/Users/simonray/DropboxUiO/dropData/text_mining/covid_pubmed_data/citation_data/uniq_cites_cleaned.tsv", sep='\t')

