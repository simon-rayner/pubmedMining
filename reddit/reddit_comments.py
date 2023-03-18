
import ast
import json
 

with open('/Users/simonray/DropboxUiO/dropData/text_mining/reddit/comment_dumps/RC_2020-02.rCOVID19') as f:
    lines = f.read().splitlines()
fOut= open("/Users/simonray/DropboxUiO/dropData/text_mining/reddit/comment_dumps/RC_2020-02.rCOVID19.tsv","w+")
fOut.write('title'
             + "\t" + "fullName" \
             + "\t" + "upvoteRatio" \
             + "\t" + "numComments" \
             + "\t" + "quarantine" \
             + "\t" + "viewCount" + "\n")
results = []

l = 0
for line in lines:
    print(str(l))
    #result = ast.literal_eval(line)
    result = json.loads(line)
    results.append(result)


    title = ""
    try:
        title = result['title']
    except:
        title = 'missing'

    fullName = ""
    try:
        fullName = result['author_fullname']
    except:
        fullName = 'missing'

    upvoteRatio = ""
    try:
        upvoteRatio = str(result['upvote_ratio'])
    except:
        upvoteRatio = 'missing'

    numComments = ""
    try:
        numComments = str(result['num_comments'])
    except:
        numComments = 'missing'

    viewCount = ""
    try:
        viewCount = str(result['view_count'])
    except:
        viewCount = 'missing'


    quarantine = ""
    try:
        quarantine = str(result['quarantine'])
    except:
        quarantine = 'missing'

    outStr = result['title'] \
             + "\t" + fullName \
             + "\t" + upvoteRatio \
             + "\t" + numComments \
             + "\t" + quarantine \
             + "\t" + viewCount + "\n"
    fOut.write(outStr)
    l+=1
fOut.close()
#print(results)
keysList = list(results[0].keys())
valuesList = list(results[0].values())
#i=0
##for key in keysList:
#    print(key, "\t", str(valuesList[i]))
#    i+=1


print('done')


#'COVID19 author:enterpriseF-love'
# COVID19 title:'Increased levels of circulating neurotoxic metabolites in patients with mild Covid19'
# COVID19 title:'At what stage are we allowed to demand answers'
