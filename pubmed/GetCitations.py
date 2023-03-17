import sys
import os

from datetime import datetime
import hashlib
import logging

from pathlib import Path

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from locale import atof, setlocale, LC_NUMERIC
from Bio import Entrez

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
    projectBaseName = Path(inputFile).stem
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
        parser.add_argument("-i", "--input_file", dest="inputfile", action="store", help="list of pubmed IDs [default: %(default)s]")
        parser.add_argument("-d", "--details_file", dest="detailsfile", action="store", help="base query string  [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

        global inputFile
        global detailsFile
        inputFile = args.inputfile
        detailsFile = args.detailsfile

        if inputFile:
            print("input file is <" + inputFile + ">")
        if detailsFile:
            print("details file is <" + detailsFile + ">")
            inputFile = detailsFile
        #print("base query string is <" + baseQueryString + ">")


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

def parseDetailsFile():
    outputFolder = os.path.dirname(inputFile)
    outputFile = os.path.join(outputFolder, os.path.basename(inputFile).split(".")[0] + "__wCitations.tsv")

    fDetails = open(detailsFile, "r")
    pubmedEntryLines = fDetails.readlines()
    fDetails .close()
    logging.info("read <" + str(len(pubmedEntryLines)) + "> lines")
    fPMIDs = open(outputFile, "w")
    fPMIDs.write("id" + "\t" + pubmedEntryLines[0].strip() + "\tcitationCount" + "\tcitationSet" + "\n")
    fPMIDs.close()


    Entrez.email = 'cyanidebunny@gmail.com'
    p=0
    for pubmedEntry in pubmedEntryLines:
        p+=1
        qPMID = pubmedEntry.split("\t")[2].strip()
        if qPMID == 'PMID':
            logging.info("hit header line")
            continue
        links = Entrez.elink(dbfrom="pubmed", id=qPMID, retmax=100000, linkname="pubmed_pubmed_citedin")
        record = Entrez.read(links)
        citationIDs = ""
        linkList=[]
        if len(record[0][u'LinkSetDb']) > 0:
            records = record[0][u'LinkSetDb'][0][u'Link']
            for link in records:
                linkList.append(link[u'Id'])
            citationIDs = ",".join(linkList)

        pubmedEntry = pubmedEntry.strip() + "\t" + str(len(linkList)) + "\t" + citationIDs + "\n"
        fPMIDs = open(outputFile, "a")
        fPMIDs.write(pubmedEntry)
        fPMIDs.close()


def parsePMIDList():
    outputFolder = os.path.dirname(inputFile)
    outputFile = os.path.join(outputFolder, os.path.basename(inputFile).split(".")[0] + "__citations.tsv")
    fPMIDs = open(outputFile, "w")
    fPMIDs.write("PMID\tCitationCount\tCitationPMIDs\n")
    fPMIDs.close()

    fRaw = open(inputFile, "r")
    qPMIDs = fRaw.readlines()
    fRaw.close()
    Entrez.email = 'cyanidebunny@gmail.com'
    for qPMID in qPMIDs:

        links = Entrez.elink(dbfrom="pubmed", id=qPMID, retmax=100000, linkname="pubmed_pubmed_citedin")
        record = Entrez.read(links)
        records = record[0][u'LinkSetDb'][0][u'Link']
        linkList=[]
        for link in records:
            linkList.append(link[u'Id'])
        citationIDs = ",".join(linkList[1:])
        fPMIDs = open(outputFile, "a")
        fPMIDs.write(linkList[0] + "\t" + str(len(citationIDs)) + "\t" + citationIDs + "\n")
        fPMIDs.close()



def main(argv=None): # IGNORE:C0111

    setlocale(LC_NUMERIC, 'no_NO')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)
    if detailsFile:
        parseDetailsFile()
    else:
        parsePMIDList()



if __name__ == '__main__':

    sys.exit(main())
