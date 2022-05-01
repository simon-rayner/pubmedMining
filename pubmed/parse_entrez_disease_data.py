import sys
import os
from datetime import datetime
import hashlib
import logging
import pandas as pd

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
    projectBaseName = diseaseListFile
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

        global diseaseListFile
        diseaseListFile = args.diseaselistfile
        global countryDataFile
        countryDataFile = args.countrydatafile
        global journalImpactFactorDataFile
        journalImpactFactorDataFile = args.journaldatafile


        print("disease list file is <" + diseaseListFile + ">")
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



def setPaths():
    #global diseaseListFile
    #global countryDataFile
    #global journalImpactFactorDataFile
    #diseaseListFile = "/Users/simonray/DropboxUiO/dropData/text_mining/entrez_searches/disease_list.tsv"
    #countryDataFile = "/Users/simonray/DropboxUiO/dropData/text_mining/entrez_searches/countries.tsv"
    #journalImpactFactorDataFile = "/Users/simonray/DropboxUiO/dropData/text_mining/entrez_searches/journal_impact_factors.tsv"
    pass

def loadDiseaseList():
    global dfDiseaseList
    fDL = open(diseaseListFile, "r")
    dfDiseaseList = fDL.read().splitlines()
    logging.info("--loaded <" + str(len(dfDiseaseList)) + "> diseases")


def loadCountryData():
    global dfCountryData
    dfCountryData = pd.read_csv(countryDataFile, sep="\t")
    dfCountryData['country'] = dfCountryData['country'].str.rstrip()
    dfCountryData['subregion'] = dfCountryData['subregion'].str.rstrip()
    dfCountryData['region'] = dfCountryData['region'].str.rstrip()



    logging.info("--loaded data for <" + str(len(dfCountryData)) + "> countries")

def loadJournalData():
    global dfJournalData
    dfJournalData = pd.read_csv(journalImpactFactorDataFile, sep="\t")

    logging.info("--loaded data for <" + str(len(dfJournalData)) + "> journals")


def parseDiseases():
    lSummaryStatsAllDiseases = []
    diseaseListSummaryFile = diseaseListFile.replace(".tsv", "_summary.tsv")
    fStats  = open(diseaseListSummaryFile, "w")
    fStats.write('disease\tIFs\tyears\tcountries\tnoOfCountries\tnoOfPublications\n')

    for diseaseFile in dfDiseaseList:
        lSummaryStatsThisDisease = []
        logging.info(diseaseFile)
        diseaseName = os.path.basename(diseaseFile).split(".")[0]
        logging.info("----parsing publications for <" + diseaseName + ">")

        dfDiseasePubSet = pd.read_csv(diseaseFile, sep="\t")
        logging.info("--loaded <" + str(len(dfDiseasePubSet)) + "> entries")
        minIF = 1000000
        maxIF = 0
        IFs=[]
        years=[]
        allCountries=[]
        missingCountryCount = 0
        for indexD, publication in dfDiseasePubSet.iterrows():
            logging.info(publication['pmid'])
            impactFactor = dfJournalData[dfJournalData['PubMed_Title'].str.upper()==publication['title'].upper()]['Journal Impact Factor']
            if len(impactFactor) > 0:
                impactFactor=atof(impactFactor)
            else:
                impactFactor = 0.0
            IFs.append(impactFactor)
            if maxIF < impactFactor: maxIF = impactFactor
            if minIF > impactFactor: minIF = impactFactor
            years.append(publication['year'])
            affiliations = publication['affiliations'].strip('][').split("', '")
            if len(affiliations) > 0:
                firstCountry = getCountryFromAffiliation(affiliations[0])
                #if not firstCountry:
                #    logging.info("------couldn't get first country information for <" +
                #                 affiliations[0] + ">")
                lastCountry = getCountryFromAffiliation(affiliations[len(affiliations)-1])
                #if not lastCountry:
                #    logging.info("------couldn't get last country information for <" +
                #                 affiliations[len(affiliations)-1] + ">")

                countrySet = []
                for affiliation in affiliations:
                    #logging.info(affiliation)
                    country = getCountryFromAffiliation(affiliation)
                    if country:
                        if country not in countrySet:
                            countrySet.append(country)
                        if country not in allCountries:
                            allCountries.append(country)
                    if not country:
                        logging.info("------couldn't get country information for <" +
                                     affiliation + ">")
                        missingCountryCount += 1

            else:
                logging.info("missing affiliation information")

            lSummaryStatsThisDisease.append({
                'PMID': publication['pmid'], 'year': publication['year'],
                'impactFactor': impactFactor,
                'firstCountry': firstCountry, 'lastCountry':lastCountry,
                'noOfCountries': len(countrySet), 'missingCountryEntries': missingCountryCount,
                'articleTitle': publication['articleTitle'], 'journal': publication['title']
                                             })
        diseaseStatsFile =  diseaseFile.replace(".tsv", "_stats.tsv")
        pd.DataFrame(lSummaryStatsThisDisease).to_csv(diseaseStatsFile)
        lSummaryStatsAllDiseases.append({
            'disease': diseaseName, 'IFs':IFs, 'years': years, 'countries': allCountries,
            'IFs': IFs, 'minIF': minIF, 'maxIF': maxIF,
             'noOfCountries': len(countrySet),
            'noOfPublications': len(dfDiseasePubSet)})
        fStats.write(diseaseName + "\t"
                                 + str(len(countrySet)) + "\t"
                                 + str(len(dfDiseasePubSet)) + "\t"
                                 + "|".join(str(i) for i in IFs) + "\t"
                                 + "|".join(str(y) for y in years) + "\t"
                                 + "|".join(str(c) for c in countrySet) + "\n")
        logging.info("-----done")
    fStats.close()


def getCountryFromAffiliation(qAffiliation):
    for indexC, countryEntry in dfCountryData.iterrows():
        for country in countryEntry['country'].split("|"):
            if country in qAffiliation:
                return countryEntry['country'].split("|")[0]
    return ""

def main(argv=None): # IGNORE:C0111
    setlocale(LC_NUMERIC, '')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)

    loadDiseaseList()
    loadCountryData()
    loadJournalData()
    parseDiseases()

    logging.info("project file is <" + diseaseListFile + ">")


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
