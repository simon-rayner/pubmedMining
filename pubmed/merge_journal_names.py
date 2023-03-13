import pandas as pd


dfJCR = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/journal_impact_factors.tsv", sep="\t")
dfPubmed = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/pubmed2IF_journalnames.tsv", sep="\t")

# in the PubMed names, select journal names that begin with 'The '

dfPubmedThe = dfPubmed[dfPubmed['PubMed_Title'].str.startswith('THE ', na=False)]
dfPubmedThe0 = dfPubmedThe[dfPubmedThe['match'] == 1]
dfPubmedMissingIF = dfPubmedThe[dfPubmedThe['match'] == 1]
dfJCR['Full Journal Title'] = dfJCR['Full Journal Title'].str.upper()

# are there PubMed names that are contained within the JCR names

hitCount = 0
for indexP, pubmedEntry in dfPubmedMissingIF.iterrows():
    dfJCR0 = dfJCR[dfJCR['Full Journal Title'].str.contains(pubmedEntry['PubMed_Title'])]
    if len(dfJCR0) > 0:
        print(str(len(dfJCR0)))
        hitCount+=1

print("got <" + str(hitCount) + "> hits from pubmed -> jcr")

hitCount = 0
for indexJ, jcrEntry in dfJCR.iterrows():
    dfPubmedMissingIF0 = dfPubmedMissingIF[dfPubmedMissingIF['PubMed_Title'].str.contains(jcrEntry['Full Journal Title'])]

    if len(dfPubmedMissingIF0) == 1:
        print(dfPubmedMissingIF0['PubMed_Title'])
        hitCount+=1

print("got <" + str(hitCount) + "> hits from jcr -> pubmed")


