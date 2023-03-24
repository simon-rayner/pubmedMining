import sys
import os
from locale import atof, setlocale, LC_NUMERIC
from datetime import datetime
import hashlib
import logging


from pathlib import Path

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

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

    projectBaseName = Path(citationFile).stem

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
        parser.add_argument("-b", "--biorxiv_file", dest="biorxivfile", action="store", help="biorxiv file containing submission metadata")
        parser.add_argument("-m", "--medrxiv_file", dest="biorxivfile", action="store", help="medrxiv file containing submission metadata")
        parser.add_argument("-c", "--citation_file", dest="citationfile", action="store", help="medrxiv file containing submission metadata")

        # Process arguments
        args = parser.parse_args()

        global biorxivFile
        global medrxivFile
        global citationFile

        biorxivFile = args.biorxivfile
        medrxivFile = args.medrxivfile
        citationFile = args.citationfile

        if biorxivFile:
            print("biorxiv file is <" + biorxivFile + ">")

        if medrxivFile:
            print("medrxiv file is <" + medrxivFile + ">")

        if citationFile:
            print("citation file is <" + citationFile + ">")

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

def loadData():

    global dfCitations
    global lBiorxivLines
    global lMedrxivLines

    dfCitations = pd.read_csv(citationFile, sep="\t")
    logging.info("read <" + str(len(dfCitations)) + "> citations")

    fBiorxiv = open(biorxivFile, "r")
    lBiorxivLines = fBiorxiv.readlines()
    logging.info("read ~ <" + str(len(lBiorxivLines)) + "> biorxiv entries")

    fMedxriv = open(medrxivFile, "r")
    lMedrxivLines = fMedxriv.readlines()
    logging.info("read <" + str(len(lMedrxivLines)) + "> medrxiv entries")


def getBiorxivDOIs():
    # get subset of Citations that are biorxiv preprints
    import json
    dfCitations['journal_name'] = ""
    biorPubCount = 0
    biorUPubCount = 0
    for index, row in dfCitations.iterrows():

        if 'biorxiv' in row['url']:
            # typical entry is of the form
            #   https://www.biorxiv.org/content/10.1101/2020.05.13.093195v1?fbclid=IwAR1Xb79A0cGjORE2nwKTEvBb7y4-NBuD5oRf2wKWZfAhoCJ8_T73QSQfskw
            # we need to extract the '10.1101/2020.05.13.093195', without the 'v' version information
            # so,
            biorxivID = row['url']
            biorxivID = biorxivID.split("/")
            biorxivIDpt1 = biorxivID.split("/")[5]
            biorxivIDpt2 = biorxivID.split("/")[6]
            biorxivIDpt2 = biorxivIDpt2.split("v")[0]
            biorxivID = biorxivIDpt1 + "/" + biorxivIDpt2

            match = False
            for bioLine in lBiorxivLines:
                if biorxivID in bioLine:
                    #'published_doi': '10.1039/D1LC00876E', 'published_journal': 'Lab on a Chip'
                    thisDict = json.loads(bioLine)
                    publishedDOI = thisDict['published_doi']
                    publishedJournal = thisDict['published_journal']

                    dfCitations.iloc[index]['doi'] = publishedDOI
                    dfCitations.iloc[index]['journal_name'] = publishedJournal
                    dfCitations.iloc[index]['pub_category'] = 'PPP'

                    match = True
                    biorPubCount += 1

                    break

            if not match:
                dfCitations.iloc[index]['doi'] = ""
                dfCitations.iloc[index]['journal_name'] = "none"
                dfCitations.iloc[index]['pub_category'] = 'PPU'
                biorUPubCount += 1

    logging.info("--found <" + str(biorPubCount + biorUPubCount) + "> biorxiv preprints")
    logging.info("------- <" + str(biorPubCount) + "> were published")
    logging.info("------- <" + str(biorUPubCount) + "> were not ")


def getMedrxivDOIs():
    # get subset of Citations that are medrxiv preprints
    import json
    dfCitations['journal_name'] = ""
    medrPubCount = 0
    medrUPubCount = 0
    for index, row in dfCitations.iterrows():

        if 'medrxiv' in row['url']:
            # typical entry is of the form
            #   https://www.medrxiv.org/content/10.1101/2020.05.13.093195v1?fbclid=IwAR1Xb79A0cGjORE2nwKTEvBb7y4-NBuD5oRf2wKWZfAhoCJ8_T73QSQfskw
            # we need to extract the '10.1101/2020.05.13.093195', without the 'v' version information
            # so,
            medrxivID = row['url']
            medrxivID = medrxivID.split("/")
            medrxivIDpt1 = medrxivID.split("/")[5]
            medrxivIDpt2 = medrxivID.split("/")[6]
            medrxivIDpt2 = medrxivIDpt2.split("v")[0]
            medrxivID = medrxivIDpt1 + "/" + medrxivIDpt2

            match = False
            for bioLine in lBiorxivLines:
                if medrxivID in bioLine:
                    #'published_doi': '10.1039/D1LC00876E', 'published_journal': 'Lab on a Chip'
                    thisDict = json.loads(bioLine)
                    publishedDOI = thisDict['published_doi']
                    publishedJournal = thisDict['published_journal']

                    dfCitations.iloc[index]['doi'] = publishedDOI
                    dfCitations.iloc[index]['journal_name'] = publishedJournal
                    dfCitations.iloc[index]['pub_category'] = 'PPP'

                    match = True
                    medrPubCount += 1
                    break

            if not match:
                dfCitations.iloc[index]['doi'] = ""
                dfCitations.iloc[index]['journal_name'] = "none"
                dfCitations.iloc[index]['pub_category'] = 'PPU'
                medrUPubCount += 1

    logging.info("--found <" + str(medrPubCount + medrUPubCount) + "> biorxiv preprints")
    logging.info("------- <" + str(medrPubCount) + "> were published")
    logging.info("------- <" + str(medrUPubCount) + "> were not ")


def writeData():
    outputFolder = os.path.dirname(citationFile)
    outputFileCounts = os.path.join(outputFolder, os.path.basename(citationFile).split(".")[0] + "__BiorMedrDOIs.tsv")
    dfCitations.to_csv(outputFileCounts, sep="\t")

def main(argv=None): # IGNORE:C0111

    setlocale(LC_NUMERIC, 'no_NO')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)
    loadData()
    getBiorxivDOIs()
    getMedrxivDOIs()
    writeData()




if __name__ == '__main__':

    sys.exit(main())
