
import ast
import json
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
    projectBaseName = ""

    projectBaseName = Path(submissionsFile).stem

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
        parser.add_argument("-c", "--comments_file", dest="commentsfile", action="store", help="list reddit submission files [default: %(default)s]")
        parser.add_argument("-s", "--submissions_file", dest="submissionsfile", action="store", help="list reddit comment files [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

        global submissionsFile
        global commentsFile
        submissionsFile = args.submissionsfile
        commentsFile = args.commentsfile

        if submissionsFile:
            print("submissions file list is <" + submissionsFile + ">")
        if commentsFile:
            print("comments file list is <" + commentsFile + ">")

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

def parseSubmissions():
    outputFolder = os.path.dirname(submissionsFile)
    outputFile = os.path.join(outputFolder, os.path.basename(submissionsFile).split(".")[0] + "_wCommentCount.tsv")
    dfSubmissions = pd.read_csv(submissionsFile, sep="\t")
    logging.info("loaded <" + str(len(dfSubmissions)) + "> submission entries")

    dfComments=pd.read_csv(commentsFile, sep="\t")
    logging.info("loaded <" + str(len(dfComments)) + "> comment entries")

    submissionsWithComments = 0
    dfSubmissions['comment_count'] = 0
    for index, submission in dfSubmissions.iterrows():
        if index%1000 == 0:
            logging.info(str(index))
        try:
            dfSubmissions.loc[index,['comment_count']] = dfComments['link_id'].value_counts()['t3_' + submission['id']]
            submissionsWithComments += 1
        except:
            continue

    logging.info("found <" + str(submissionsWithComments) + "> submissions with comments")
    dfSubmissions.to_csv(outputFile, sep="\t")


def slowParseComments():
    fSubmissions = open(commentsFile, "r")
    submissionLines = fSubmissions.readlines()
    s=0
    for submissionLine in submissionLines:
        linkID=""
        id=""
        try:
            linkID = submissionLine.split("\t")[3]
            id = submissionLine.split("\t")[2]
        except:
            logging.info(submissionLine)

        s+=1
        logging.info(str(s) + ":--[" + id + "<-->" + linkID + "]" )


def main(argv=None): # IGNORE:C0111

    setlocale(LC_NUMERIC, 'no_NO')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)
    parseSubmissions()




if __name__ == '__main__':

    sys.exit(main())
