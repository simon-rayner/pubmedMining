from Bio import Entrez
import csv
import pandas as pd
import os
import sys

# see here for more info
# https://biopython-tutorial.readthedocs.io/en/latest/notebooks/09%20-%20Accessing%20NCBIs%20Entrez%20databases.html

def search(query, qMindate, qMaxdate):
    Entrez.email = 'cyanidebunny@gmail.com'
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax='10000',
                            mindate=qMindate,
                            maxdate=qMaxdate,
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list, qMindate, qMaxdate):
    ids = ','.join(id_list)
    Entrez.email = 'cyanidebunny@gmail.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           mindate=qMindate,
                           maxdate=qMaxdate,
                           id=ids,
                           retmax=10000)
    results = Entrez.read(handle)
    return results


def parseDiseaseList(diseaseList, outputFolder, fStats):
    for diseaseString in diseaseList:
        print("parsing <" + diseaseString + ">" )

        results = search(diseaseString + "[TIAB]", 0, 2025)
        id_list = results['IdList']
        if(len(id_list) != 0):
            papers = fetch_details(id_list, 0, 2025)
            parseDiseaseSet(papers, diseaseString, outputFolder, fStats)
        else:
            print("---- found <0> articles"  )
            #diseaseCount.append({"disease":diseaseString, "paperCount":0})
            fStats.write(diseaseString + "\t" + "0" + "\n")



def loadDiseaseList(diseaseListFile):
    f = open(diseaseListFile, "r")
    return f.read().splitlines()


def parseDiseaseSet(papers, diseaseString, outputFolder, fStats):
    print("---- found <" + str(len(papers['PubmedArticle'])) + "> articles"  )
    fStats.write(diseaseString + "\t" + str(len(papers['PubmedArticle'])) + "\n")
    diseaseCount.append({"disease":diseaseString, "paperCount":len(papers['PubmedArticle'])})
    paperSet = []
    yearCountA = 0
    yearCountP = 0
    for i, paper in enumerate(papers['PubmedArticle']):
        #print("{}) {}".format(i+1, paper['MedlineCitation']['Article']['ArticleTitle']))
        #print (i)
        pmid = "".join(paper['MedlineCitation']['PMID'])
        affiliations=[]
        authorCount=0
        if 'AuthorList' in paper['MedlineCitation']['Article']:
            authorCount=len(paper['MedlineCitation']['Article']['AuthorList'])
            a=0

            while a < len(paper['MedlineCitation']['Article']['AuthorList']):
                if len(paper['MedlineCitation']['Article']['AuthorList'][a]['AffiliationInfo']) >0:
                    authorAffiliation = paper['MedlineCitation']['Article']['AuthorList'][a]['AffiliationInfo'][0]['Affiliation']
                    if authorAffiliation not in affiliations:
                        affiliations.append(authorAffiliation)
                a+=1

        #paper['MedlineCitation']['Article']['AuthorList'][0]['AffiliationInfo'][0]['Affiliation']
        year = '0'
        if len(paper['MedlineCitation']['Article']['ArticleDate']) > 0:
            year = paper['MedlineCitation']['Article']['ArticleDate'][0]['Year']
            yearCountA+=1
        #print(str(year) + ":" + str(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']))
        if year == '0':
            try:
               year = str(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year'])
               yearCountP += 1
            except:
                pass


        title = paper['MedlineCitation']['Article']['Journal']['Title']
        articleTitle = paper['MedlineCitation']['Article']['ArticleTitle']
        #if paper['MedlineCitation']['Article']['Abstract']
        abstract=""
        if 'Abstract' in paper['MedlineCitation']['Article']:
            abstract = paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0]

        paperSet.append({'pmid': pmid, 'year':year, 'title':title,
                         'authorCount': authorCount, 'articleTitle':articleTitle,
                         'abstract':abstract, 'affiliations': affiliations})
    print(str(yearCountA) + ":" + str(yearCountP))


    dfPaperSet = pd.DataFrame(paperSet)
    resultsFile=os.path.join(outputFolder, diseaseString.replace(" ", "_") + ".tsv")
    dfPaperSet.to_csv(resultsFile, sep="\t", encoding='utf-8')


if __name__ == '__main__':
    global diseaseCount
    diseaseCount = []
    diseaseSummaryFile = "/Users/simonray/DropboxUiO/dropData/text_mining/rift_valley_diseases.txt"
    print("disease list file is <" + diseaseSummaryFile + ">")
    outputFolder = "/Users/simonray/DropboxUiO/dropData/text_mining/20220512_moreyears"
    print("output folder is <" + outputFolder + ">")
    #outputFolder = os.path.dirname(diseaseSummaryFile)

    summaryStatsFile = os.path.join(outputFolder, os.path.basename(diseaseSummaryFile).split(".")[0] + "_counts.tsv")
    print("summaryStatsFile is <" + summaryStatsFile + ">")

    fStats = open(summaryStatsFile, "w")
    fStats.write("Disease" + "\t" + "PublicationCount" + "\n")
    diseaseList = loadDiseaseList(diseaseSummaryFile)
    print("loaded <" + str(len(diseaseList)) + "> diseases")

    parseDiseaseList(diseaseList, outputFolder, fStats)
    # Example query string is:
    # "patient physician relationship"[tiab:~0] OR "patient doctor relationship"[tiab:~0]
    # TIAB corresponds to hits in the title/abstract field
    # ~0 means the words have to be adjacent
    # Search string is case insensitive

    fStats.close()
    print("done")

    sys.exit(0)





