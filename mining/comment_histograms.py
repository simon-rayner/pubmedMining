import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import numpy as np


dfComments = pd.read_csv("/Users/simonray/DropboxUiO/dropData/text_mining/reddit/submission_dumps/comment_counts.tsv", sep="\t")

plt.hist(dfComments['ALL_POSTS'],
         bins=np.arange(0, 500, 25),
         alpha=0.5, # the transaparency parameter
         label='all_posts')

plt.hist(dfComments['NO_REDDIT'],
         bins=np.arange(0, 500, 25),
         alpha=0.5,
         label='no Reddit')

plt.legend(loc='upper right')
plt.title('Comments before and after cleanup')

plt.savefig("/Users/simonray/DropboxUiO/dropData/text_mining/reddit/submission_dumps/comment_counts_0to500.png")
plt.show()
print("done")
