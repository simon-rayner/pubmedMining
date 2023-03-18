

from pmaw import PushshiftAPI
import json
api = PushshiftAPI()
import datetime as dt

start_epoch=int(dt.datetime(2020, 1, 1).timestamp())
end_epoch=int(dt.datetime(2020, 1, 10).timestamp())
#api_request_generator = api.search_comments(q='(Shakespeare)&(Beyonce)"', after = start_epoch, before=end_epoch)

posts = api.search_submissions(subreddit="COVID19", limit=2000, mem_safe=True, after = start_epoch, before=end_epoch)
post_list = [post for post in posts]

print("found <" + str(len(post_list)) + ">")

fOut = open("/Users/simonray/DropboxUiO/DResearch/text_mining/COVID19_100000b.txt", "w+")
for post in post_list:
    fOut.write(json.dumps(post) + "\n")
fOut.close()

#https://api.pushshift.io/reddit/submission/search?q=COVID19&before=8h&after=9h&size=500&subreddit=COVID19
