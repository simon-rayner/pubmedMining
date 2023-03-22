
import json
import sys
import os
from locale import atof, setlocale, LC_NUMERIC
from datetime import datetime
import hashlib
import logging
from sklearn.decomposition import TruncatedSVD
import seaborn as sns
from pathlib import Path

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from scipy.sparse import csr_matrix
import requests

__all__ = []
__version__ = 0.1
__date__ = '2022-04-19'
__updated__ = '2022-04-19'

import pandas as pd

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def initLogger(md5string):

    ''' setup log file based on project name'''
    projectBaseName = ""

    projectBaseName = Path(citationsFile).stem

    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M%S")
    logFolder = os.path.join(os.getcwd(), "logfiles")
    if not os.path.exists(logFolder):
        print("--log folder <" + logFolder + "> doesn't exist, creating")
        os.makedirs(logFolder)
    logfileName = os.path.join(logFolder, projectBaseName + "__" + dt_string + "__" + md5string +".log")
    handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(level=logging.DEBUG)

    fileh = logging.FileHandler(logfileName, 'a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileh.setFormatter(formatter)

    log = logging.getLogger()  # root logger
    log.setLevel(logging.DEBUG)
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)
    log.addHandler(fileh)      # set the new handler
    log.addHandler(handler)
    logging.info("+" + "*"*78 + "+")
    logging.info("project log file is <" + logfileName + ">")
    logging.info("+" + "*"*78 + "+")
    logging.debug("debug mode is on")


def parseArgs(argv):
    '''parse out Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    #program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s
    i
      Created by Simon Rayner on %s.
      Copyright 2023 Oslo University Hospital. All rights reserved.
    
      Licensed under the Apache License 2.0
      http://www.apache.org/licenses/LICENSE-2.0
    
      Distributed on an "AS IS" basis without warranties
      or conditions of any kind, either express or implied.
    
    USAGE
    ''' % (program_name, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-i","--citations_file", dest="citationsfile", action="store", help="list of citations [default: %(default)s]")
        parser.add_argument('-n','--ncomponents', dest="ncomponents", action="store", help= 'Number of components to use', default=5)
        parser.add_argument('-c','--cluster', dest="cluster", action="store", help= 'Number of clusters to use', default=3)
        parser.add_argument('-m','--mode', dest="mode", action="store", help= 'Test, kcluster (K-Means Clustering) or acluster(Agglomerative Clustering *)')
        parser.add_argument('-a','--affinity', dest="affinity", action="store", help= 'To be used along with Agglomerative Clustering. Can be “euclidean”, “l1”, “l2”, “manhattan”, “cosine”, default is cosine', default='cosine')
        parser.add_argument('-l','--abstract_length', dest="minabstractlength", action="store", help= 'min abstract length', default=100)

        # Process arguments
        args = parser.parse_args()

        global citationsFile
        global ncomponents
        global ncluster
        global mode
        global affinity
        global minAbstractLength


        citationsFile = args.citationsfile

        ncomponents = 5
        if args.ncomponents:
            ncomponents = args.ncomponents

        ncluster = 3
        if args.cluster:
            ncluster = args.cluster
        mode = args.mode
        affinity = args.affinity

        minAbstractLength = args.minabstractlength

        #source = args.source

        print("citationsFile file is <" + citationsFile + ">")
        #print("source is <" + source + ">")

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        print(e)
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

def test(variance,X,ncomponents):
    import matplotlib.pyplot as plt
    from sklearn.decomposition import TruncatedSVD
    tsvd = TruncatedSVD(n_components=ncomponents)
    fig, (ax1, ax2) = plt.subplots(2,1)
    PC = range(1, tsvd.n_components+1)
    ax1.bar(PC, variance, color='red')


    ##Kmeans inertias evaluation
    from sklearn.cluster import KMeans
    inertias = []
    for k in range(1,10):
        model = KMeans(n_clusters=k)
        model.fit(X[:,:3])
        inertias.append(model.inertia_)
    ##Plot
    ax2.plot(range(1,10), inertias, '-p', color='red')
    ax1.set_title('PCA Components')
    ax2.set_title('Clusters')
    plt.show()
    return()

def loadCitations():
    global dfCitations
    dfRaw=pd.read_csv(citationsFile, sep='\t')

    logging.info("read <" + str(len(dfRaw)) + "> citation entries ")
    dfCitations = dfRaw[dfRaw['articleAbstract'].str.len()>minAbstractLength]
    logging.info("after filtering for short abstracts have <" + str(len(dfCitations)) + "> citation entries ")


def calcCitationSimilarities():
    countvectorizer = TfidfVectorizer(stop_words='english')
    data=dfCitations['articleAbstract']


    vector = countvectorizer.fit_transform(data)
    vnames=countvectorizer.get_feature_names_out()
    X=wm2df(vector,vnames)

    tsvd = TruncatedSVD(n_components=ncomponents)
    X_sparse = csr_matrix(X)
    X_sparse_tsvd = tsvd.fit(X_sparse).transform(X_sparse)

    #for index, row in dfCitations.iterrows():

    #### 2d Plots #############
    #sns.scatterplot(x=X_sparse_tsvd[:,1], y=X_sparse_tsvd[:,2], alpha=0.3)

    #########################

    if mode=='test':
        ###PCA componentsevaluation
        test(tsvd.explained_variance_ratio_,X_sparse_tsvd,ncomponents)


    if mode=='kcluster':
        #Cluster by Kmeans
        cluster(ncluster, X_sparse_tsvd, dfCitations['PMID'])


    #Calculate the distance matrix
    if mode=="acluster":
        cosinef(X,X_sparse_tsvd,ncluster,dfCitations['PMID'])


###Cluster by Kmeans
def cluster(ncluster,X,pmid):
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    model = KMeans(n_clusters=ncluster)
    model.fit(X[:,:2])
    labels = model.predict(X[:,:2])

    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(X[:,0],X[:,1],X[:,2], c=labels)
    for i in range(0,len(pmid)):
        ax.text(X[i,0],X[i,1],X[i,2],pmid[i], size=8)
    plt.show()

    return()

####Cosine similarity
def cosinef(X,Xs,ncluster,pmid):
    from sklearn.cluster import AgglomerativeClustering
    import matplotlib.pyplot as plt
    model=AgglomerativeClustering(affinity='cosine',n_clusters=ncluster,linkage='complete').fit(X)
    labels=model.labels_
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(Xs[:,0],Xs[:,1],Xs[:,2], c=labels)
    for i in range(0,len(pmid)):
        ax.text(Xs[i,0],Xs[i,1],Xs[i,2],pmid[i], size=8)
    plt.show()
    return()

def wm2df(wm, feat_names):
    import pandas as pd
    # create an index for each row
    doc_names = ['Doc{:d}'.format(idx) for idx, _ in enumerate(wm)]
    df = pd.DataFrame(data=wm.toarray(), index=doc_names,
                      columns=feat_names)
    return(df)

def main(argv=None): # IGNORE:C0111

    setlocale(LC_NUMERIC, 'no_NO')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)
    loadCitations()
    calcCitationSimilarities()




if __name__ == '__main__':

    sys.exit(main())
