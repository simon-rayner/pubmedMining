
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
from sklearn.decomposition import PCA
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
        parser.add_argument('-a','--affinity', dest="affinity", action="store", help= 'To be used along with Agglomerative Clustering. Can be “euclidean”, “l1”, “l2”, “manhattan”, “cosine”, default is cosine', default='cosine')
        parser.add_argument('-l','--abstract_length', dest="minabstractlength", action="store", help= 'min abstract length', default=100)
        parser.add_argument('-w','--window_size', dest="windowsize", action="store", help= 'sliding window size for sampling citations', default=400)
        parser.add_argument('-s','--step_size', dest="stepsize", action="store", help= 'step size for sliding window', default=10)


        # Process arguments
        args = parser.parse_args()

        global citationsFile
        global ncomponents
        global ncluster
        global affinity
        global minAbstractLength
        global windowSize
        global stepSize


        citationsFile = args.citationsfile
        ncomponents = args.ncomponents
        ncluster = args.cluster
        affinity = args.affinity
        minAbstractLength = args.minabstractlength
        windowSize = args.windowsize
        stepSize = args.stepsize

        print("citationsFile file is <" + citationsFile + ">")
        print("ncomponents is <" + str(ncomponents) + ">")
        print("number of clusters is <" + str(ncluster) + ">")
        print("affinity is <" + str(affinity) + ">")
        print("minimum abstract length is <" + str(minAbstractLength) + ">")
        print("window size is <" + str(windowSize) + ">")
        print("step size is <" + str(stepSize) + ">")

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

def loadCitations():
    global dfCitations
    dfRaw=pd.read_csv(citationsFile, sep='\t')

    logging.info("read <" + str(len(dfRaw)) + "> citation entries ")
    dfCitations = dfRaw[dfRaw['articleAbstract'].str.len()>minAbstractLength]
    logging.info("after filtering for short abstracts have <" + str(len(dfCitations)) + "> citation entries ")

def calcCitationSimilarities():
    from io import BytesIO
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    countvectorizer = TfidfVectorizer(stop_words='english')

    data=dfCitations['articleAbstract']

    startRow = 0
    outputFolder = os.path.dirname(citationsFile)
    outputFileCountPrecursor = os.path.join(outputFolder, os.path.basename(citationsFile).split(".")[0])
    noOfIterations = (len(dfCitations['articleAbstract']) - windowSize)/stepSize
    inc = 0
    while startRow + windowSize < len(dfCitations['articleAbstract']):
        logging.info("processing <" + str(inc) + "> of <" + str(int(noOfIterations)) + "> iterations")
        dfSubSet = dfCitations[startRow:startRow + windowSize]['articleAbstract']
        vectorSubSet = countvectorizer.fit_transform(dfSubSet)
        vnamesSubSet = countvectorizer.get_feature_names_out()
        dfWordMatrixSubSet = wm2df(vectorSubSet,vnamesSubSet)
        startRow += stepSize
        tsvdSubSet = TruncatedSVD(n_components=ncomponents)
        dfSparseWordMatrixSubSet = csr_matrix(dfWordMatrixSubSet)
        X_sparse_tsvd = tsvdSubSet.fit(dfSparseWordMatrixSubSet).transform(dfSparseWordMatrixSubSet)


        # PCA analysis
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        pca = PCA(n_components = 2)
        pcaFeatures = pca.fit_transform(X_sparse_tsvd)

        dfPCA = pd.DataFrame(
            data=pcaFeatures,
            columns=['PC1', 'PC2'])
        X_principal = pca.fit_transform(X_sparse_tsvd)
        X_principal = pd.DataFrame(X_principal)
        X_principal.columns = ['P1', 'P2']
        import matplotlib.pyplot as plt
        dfPCA['title']=dfCitations[startRow:startRow + windowSize]['articleTitle']
        dfPCA['abstract']=dfCitations[startRow:startRow + windowSize]['articleAbstract']
        dfPCA['ID']=dfCitations[startRow:startRow + windowSize]['PMID']
        dfPCA.to_csv(outputFileCountPrecursor + "__" + str(inc) + ".tsv", sep="\t")
        sns.set()
        sns.lmplot(
            x='PC1',
            y='PC2',
            data=dfPCA,
            fit_reg=False,
            legend=True,
            )
        plt.ylim(-0.5, 0.5)
        plt.xlim(-0.5, 0.5)
        plt.title(os.path.basename(citationsFile).split(".")[0] + ":" + str(inc) + ":" + str(startRow + windowSize))
        #plt.show()
        plt.savefig(outputFileCountPrecursor + "__" + str(inc) + ".png")
        plt.close()
        inc += 1


    vector = countvectorizer.fit_transform(data)
    vnames=countvectorizer.get_feature_names_out()
    X=wm2df(vector,vnames)

    tsvd = TruncatedSVD(n_components=ncomponents)
    X_sparse = csr_matrix(X)
    X_sparse_tsvd = tsvd.fit(X_sparse).transform(X_sparse)
    from sklearn.decomposition import PCA
    pca = PCA(n_components = 2)
    pcaFeatures = pca.fit_transform(X_sparse_tsvd)

    dfPCA = pd.DataFrame(
        data=pcaFeatures,
        columns=['PC1', 'PC2'])

    sns.set()
    sns.lmplot(
        x='PC1',
        y='PC2',
        data=dfPCA,
        hue='target',
        fit_reg=False,
        legend=True
        )


    import matplotlib.pyplot as plt
    plt.figure(figsize =(8, 8))
    plt.title('Visualising the data')
    import scipy.cluster.hierarchy as shc
    Dendrogram = shc.dendrogram((shc.linkage(X_principal, method ='ward')))
    #for index, row in dfCitations.iterrows():

    #### 2d Plots #############
    #sns.scatterplot(x=X_sparse_tsvd[:,1], y=X_sparse_tsvd[:,2], alpha=0.3)
    from sklearn.cluster import AgglomerativeClustering
    ac2 = AgglomerativeClustering(n_clusters = 2)
    ac3 = AgglomerativeClustering(n_clusters = 3)
    ac4 = AgglomerativeClustering(n_clusters = 4)
    ac5 = AgglomerativeClustering(n_clusters = 5)
    ac6 = AgglomerativeClustering(n_clusters = 6)
    plt.figure(figsize =(6, 6))
    plt.scatter(X_principal['P1'], X_principal['P2'],
               c = ac2.fit_predict(X_principal), cmap ='rainbow')
    plt.show()
    #########################
    from sklearn.metrics import silhouette_score
    silhouette_scores = []
    silhouette_scores.append(
            silhouette_score(X_principal, ac2.fit_predict(X_principal)))
    silhouette_scores.append(
            silhouette_score(X_principal, ac3.fit_predict(X_principal)))
    silhouette_scores.append(
            silhouette_score(X_principal, ac4.fit_predict(X_principal)))
    silhouette_scores.append(
            silhouette_score(X_principal, ac5.fit_predict(X_principal)))
    silhouette_scores.append(
            silhouette_score(X_principal, ac6.fit_predict(X_principal)))

    k = [2, 3, 4, 5, 6]
    plt.bar(k, silhouette_scores)
    plt.xlabel('Number of clusters', fontsize = 20)
    plt.ylabel('S(i)', fontsize = 20)
    plt.show()




    #Cluster by Kmeans
    model =cluster(ncluster, X_sparse_tsvd)
    labels = model.predict(X[:,:2])
    plotCluster(labels, X, dfCitations['PMID'])


    cosinef(X,X_sparse_tsvd,ncluster,dfCitations['PMID'])


###Cluster by Kmeans
def cluster(ncluster,X):
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    model = KMeans(n_clusters=ncluster)
    model.fit(X[:,:2])

    return model

def plotCluster(labels, X, pmid):
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(X[:,0],X[:,1],X[:,2], c=labels)
    for i in range(0,len(pmid)):
        ax.text(X[i,0],X[i,1],X[i,2],pmid[i], size=8)
    plt.show()



####Cosine similarity
def cosinef(X,Xs,ncluster,pmid):
    from sklearn.cluster import AgglomerativeClustering
    import matplotlib.pyplot as plt
    model=AgglomerativeClustering(metric='cosine',n_clusters=ncluster,linkage='complete').fit(X)
    labels=model.labels_
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = Axes3D(fig)
    auto_add_to_figure=False
    fig.add_axes(ax, auto_add_to_figure=False)
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
