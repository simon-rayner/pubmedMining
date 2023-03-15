import sys
import os
from Bio import Entrez
from datetime import datetime
import hashlib
import logging
import pandas as pd
from pathlib import Path

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from locale import atof, setlocale, LC_NUMERIC


__all__ = []
__version__ = 0.1
__date__ = '2022-04-19'
__updated__ = '2022-04-19'

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
    projectBaseName = Path(dateRangesFile).stem
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
        parser.add_argument("-d", "--disease_list_file", dest="daterangesfile", action="store", help="list of ranges to use in entrez queries [default: %(default)s]")
        parser.add_argument("-q", "--query_string", dest="basequerystring", action="store", help="base query string  [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

        global dateRangesFile
        global baseQueryString
        dateRangesFile = args.daterangesfile
        baseQueryString = args.basequerystring

        print("date ranges file is <" + dateRangesFile + ">")
        print("base query string is <" + baseQueryString + ">")


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


def loadDateRanges():
    global dateRanges
    fDates = open(dateRangesFile, "r")
    dateRanges = fDates.readlines()
    fDates.close()
    logging.info("--loaded <" + str(len(dateRanges)) + "> dates")


def queryDateRanges():
    global dfCovidPubsByWeek
    lCovidPubsByWeek = []
    totalPublications = 0
    outputFolder = os.path.dirname(dateRangesFile)

    for dateRange in dateRanges:

        startDate = dateRange.split("\t")[0].strip()
        endDate = dateRange.split("\t")[1].strip()
        logging.info("processing <" + startDate + "-->" + endDate + ">")
        qQuery = buildEntrezDateRangeQuery(baseQueryString, startDate, endDate)
        qResult = submitEntrezQuery(qQuery)
        ids = qResult['IdList'][0:2]
        totalPublications += len(ids)
        detailedResults = fetchDetailsForIDlist(ids, startDate, endDate)
        detailedResultsFile = os.path.join(outputFolder, os.path.basename(dateRangesFile).split(".")[0]
                + "__" + startDate.replace("/","") + "__" + endDate.replace("/","") + ".xml")
        with open(detailedResultsFile, "w") as fXML:
            fXML.write(str(detailedResults))

        lCovidPubsByWeek.append({"startDate": startDate, "endDate": endDate, "numberOfPublications": len(qResult['IdList']), "totalPublications":totalPublications})
    dfCovidPubsByWeek = pd.DataFrame(lCovidPubsByWeek)


def fetchDetailsForIDlist(id_list, qMindate, qMaxdate):
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

def writeQuerySummaryResults():
    outputFolder = os.path.dirname(dateRangesFile)
    summaryStatsFile = os.path.join(outputFolder, os.path.basename(dateRangesFile).split(".")[0] + "_pubcounts.tsv")
    dfCovidPubsByWeek.to_csv(summaryStatsFile, sep="\t")


def buildEntrezDateRangeQuery(queryString, startDate, endDate):
    #query='("patient physician relationship"[tiab:~0] OR "patient doctor relationship"[tiab:~0]) AND (("2022/05/01"[Date - Publication] : "2022/05/08"[Date - Publication]))'
    query = '(' + queryString + ') AND (' + '("' + startDate + '"[Date - Publication]' + ' : "' + endDate + '"[Date - Publication])' + ")"
    return query

def submitEntrezQuery(query):
    Entrez.email = 'cyanidebunny@gmail.com'
    qMindate = 0
    qMaxdate = 2025
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax='10000',
                            mindate=qMindate,
                            maxdate=qMaxdate,
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    return results

def main(argv=None): # IGNORE:C0111

    setlocale(LC_NUMERIC, 'no_NO')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)
    loadDateRanges()
    queryDateRanges()
    writeQuerySummaryResults()


if __name__ == '__main__':

    sys.exit(main())
