# Introduction

this project is a loose collection of Python scripts for looking at publication data in 
PubMed.

Currently, there are two goals. 

1. what is the range of publications on animals diseases?
2. what is the range of publications on covid?

## Covid-19 Publications

There are a huge number of publications on covid-19/coronaviruses. 
PubMed has a 10000 limit on downloaded data, so need to use their
API to handle this and pull down the data in weekly bites

the script `covid_count.py` reads in this file and 
then generates API queries using a query string of the form

```
q2 = '("covid"[Title/Abstract:] OR "coronavirus"[Title/Abstract:] ) 
  AND (("2021/05/01"[Date - Publication] : "2021/05/08"[Date - Publication]))'
```

```
-d /Users/simonray/DropboxUiO/dropData/text_mining/covid_pubmed_data/covid_date_ranges_for_search.tsv  
-q "'("covid"[Title/Abstract:] OR "coronavirus"[Title/Abstract:])"
```


## Other useful stuff
Note, you can specify word proximity using the `~1` parameter

For example:

```
query='("patient physician relationship"[tiab:~1] OR "patient doctor relationship"[tiab:~1]) 
  AND (("2022/05/01"[Date - Publication] : "2022/05/08"[Date - Publication]))'
```
(here, this states that the words `patient` and `physician` and `relationship` 
must be separated by a maximum of one word in the Abstract for the 
manuscript to be included in the search results.
