import sys
import os
from datetime import datetime
import hashlib
import logging
import pandas as pd
import numpy

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
    projectBaseName = diseaseSummaryFile
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
      Copyright 2022 Oslo University Hospital. All rights reserved.
    
      Licensed under the Apache License 2.0
      http://www.apache.org/licenses/LICENSE-2.0
    
      Distributed on an "AS IS" basis without warranties
      or conditions of any kind, either express or implied.
    
    USAGE
    ''' % (program_name, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--disease_list_file", dest="diseaselistfile", action="store", help="list of diseases with entrez results [default: %(default)s]")
        parser.add_argument("-c", "--country_data_file", dest="countrydatafile", action="store", help="country data file [default: %(default)s]")
        parser.add_argument("-j", "--journal_data_file", dest="journaldatafile", action="store", help="journal data file [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

        global diseaseSummaryFile
        diseaseSummaryFile = args.diseaselistfile
        global countryDataFile
        countryDataFile = args.countrydatafile
        global journalImpactFactorDataFile
        journalImpactFactorDataFile = args.journaldatafile


        print("disease summary file is <" + diseaseSummaryFile + ">")
        print("country data file is <" + countryDataFile + ">")
        print("journal data file is <" + journalImpactFactorDataFile + ">")

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


def loadDiseaseSummary():
    global dfDiseaseSummary
    fDL = open(diseaseSummaryFile, "r")
    dfDiseaseList = fDL.read().splitlines()
    logging.info("--loaded <" + str(len(dfDiseaseList)) + "> diseases")

def plotBarChartSummary():
    dfDiseaseList['disease'].value_counts().plot(kind='barh', figsize=(8, 6))
    plt.xlabel("Count of Tips Received", labelpad=14)
    plt.ylabel("Day of Week", labelpad=14)
    plt.title("Count of Tips by Day of Week", y=1.02);

def main(argv=None): # IGNORE:C0111

    setlocale(LC_NUMERIC, 'no_NO')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)
    loadDiseaseSummary()

if __name__ == '__main__':

    if DEBUG:
        pass
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'fairpype.virusPipe_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)

    sys.exit(main())

    # 1. load a list of disease stats
    # 2. load a list of countries with regional grouping
    # 3. load a list of journals with their recent impact factor
    #
    # for disease stats. For each paper Parse out country from affiliation and get
    #     (i)    number of publications/year
    #     (ii)   total number of countries
    #     (iii)  first and last country
    #     (iv)   use country data to get first and last region, total number of regions
    #     (v)    get (current) impact factor of journal in which paper was published
    #
    #
    #global diseaseCount
    #diseaseCount = []
    #diseaseListFile="/Users/simonray/DropboxUiO/dropData/text_mining/animal_virus_list-shortnames.txt"



    #outputFolder = os.path.dirname(diseaseListFile)
    #summaryStatsFile = os.path.join(outputFolder, os.path.basename(diseaseListFile).split(".")[0]+ "_stats.tsv" )
    #fStats  = open(summaryStatsFile, "w")
    #fStats.write("Disease" + "\t" + "PublicationCount" + "\n")



    fStats.close()
    print("done")

    sys.exit(0)
