
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
    if submissionsFileList:
        projectBaseName = Path(submissionsFileList).stem
    else:
        projectBaseName = Path(commentsFileList).stem
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
        parser.add_argument("-c", "--comments_file_list", dest="commentsfilelist", action="store", help="list reddit submission files [default: %(default)s]")
        parser.add_argument("-s", "--submissions_file_list", dest="submissionsfilelist", action="store", help="list reddit comment files [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

        global submissionsFileList
        global commentsFileList
        submissionsFileList = args.submissionsfilelist
        commentsFileList = args.commentsfilelist

        if submissionsFileList:
            print("submissions file list is <" + submissionsFileList + ">")
        if commentsFileList:
            print("comments file list is <" + commentsFileList + ">")
            commentsFileList = commentsFileList

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

def parseSubmissionFileList():

    fSubmissions = open(submissionsFileList, "r")
    submissionFiles = fSubmissions.readlines()
    fSubmissions .close()
    logging.info("read <" + str(len(submissionFiles)) + "> filenames")

    fullKeyList = []

    s=1
    for submissionFile in submissionFiles:
        submissionLines = []
        with open(submissionFile.strip()) as fSubmission:
            submissionLines = fSubmission.read().splitlines()

        results = []
        logging.info("reading <" + submissionFile + ">")
        outputFolder = os.path.dirname(submissionFile)
        outputFile = os.path.join(outputFolder, os.path.basename(submissionFile).split(".")[0] + ".tsv")
        fOut= open(outputFile,"w+")
        fOut.write(getSubmissionHeaderLine())

        print(str(s))
        for submissionLine in submissionLines:
            result = json.loads(submissionLine)
            keysList = list(result.keys())
            valuesList = list(result.values())
            #logging.info("found <" + str(len(keysList)) + "> keys")
            diff = list(set(keysList) - set(fullKeyList))
            if len(diff) > 0:
                logging.info("found <" + str(len(diff)) + "> new keys")
                logging.info(diff)
                fullKeyList.extend(diff)


            ### Author
            author = ""
            try:
                author = result['author']
            except:
                author = 'missing'

            ### category
            category = ""
            try:
                category = result['category']
            except:
                category = 'missing'

            ### contest_mode
            contest_mode = ""
            try:
                contest_mode = result['contest_mode']
            except:
                contest_mode = 'missing'

            ### created_utc
            created_utc = ""
            try:
                created_utc = result['created_utc']
            except:
                created_utc = 'missing'

            ### crosspost_parent
            crosspost_parent = ""
            try:
                crosspost_parent = result['crosspost_parent']
            except:
                crosspost_parent = 'missing'

            ### discussion_type
            discussion_type = ""
            try:
                discussion_type = result['discussion_type']
            except:
                discussion_type = 'missing'

            ### distinguished
            distinguished = ""
            try:
                distinguished = result['distinguished']
            except:
                distinguished = 'missing'

            ### gilded
            gilded = ""
            try:
                gilded = result['gilded']
            except:
                gilded = 'missing'

            ### contest_mode
            contest_mode = ""
            try:
                contest_mode = result['contest_mode']
            except:
                contest_mode = 'missing'

            ### id
            id = ""
            try:
                id = result['id']
            except:
                id = 'missing'

            ### locked
            locked = ""
            try:
                locked = result['locked']
            except:
                locked = 'missing'

            ### contest_mode
            contest_mode = ""
            try:
                contest_mode = result['contest_mode']
            except:
                contest_mode = 'missing'

            ### no_follow
            no_follow = ""
            try:
                no_follow = result['no_follow']
            except:
                no_follow = 'missing'

            ### num_comments
            num_comments = ""
            try:
                num_comments = result['num_comments']
            except:
                num_comments = 'missing'

            ### num_crossposts
            num_crossposts = ""
            try:
                num_crossposts = result['num_crossposts']
            except:
                num_crossposts = 'missing'

            ### over_18
            over_18 = ""
            try:
                over_18 = result['over_18']
            except:
                over_18 = 'missing'

            ### permalink
            permalink = ""
            try:
                permalink = result['permalink']
            except:
                permalink = 'missing'

            ### pwls
            pwls = ""
            try:
                pwls = result['pwls']
            except:
                pwls = 'pwls'

            ### quarantine
            quarantine = ""
            try:
                quarantine = result['quarantine']
            except:
                quarantine = 'missing'

            ### removal_reason
            removal_reason = ""
            try:
                removal_reason = result['removal_reason']
            except:
                removal_reason = 'missing'

            ### removed_by
            removed_by = ""
            try:
                removed_by = result['removed_by']
            except:
                removed_by = 'missing'

            ### removed_by_category
            removed_by_category = ""
            try:
                removed_by_category = result['removed_by_category']
            except:
                removed_by_category = 'missing'

            ### retrieved_on
            retrieved_on = ""
            try:
                retrieved_on = result['retrieved_on']
            except:
                retrieved_on = 'missing'

            ### score
            score = ""
            try:
                score = result['score']
            except:
                score = 'missing'

            ### selftext
            selftext = ""
            try:
                selftext = result['selftext']
            except:
                selftext = 'missing'

            ### subreddit_subscribers
            subreddit_subscribers = ""
            try:
                subreddit_subscribers = result['subreddit_subscribers']
            except:
                subreddit_subscribers = 'missing'

            ### url
            url = ""
            try:
                url = result['url']
            except:
                url = 'missing'

            ### total_awards_received
            total_awards_received = ""
            try:
                total_awards_received = result['total_awards_received']
            except:
                total_awards_received = 'missing'

            title = ""
            try:
                title = result['title']
            except:
                title = 'missing'

            fullName = ""
            try:
                fullName = result['author_fullname']
            except:
                fullName = 'missing'

            upvoteRatio = ""
            try:
                upvoteRatio = str(result['upvote_ratio'])
            except:
                upvoteRatio = 'missing'


            viewCount = ""
            try:
                viewCount = str(result['view_count'])
            except:
                viewCount = 'missing'

            outputLine = title \
                     + "\t" + str(fullName) \
                     + "\t" + str(upvoteRatio) \
                     + "\t" + str(num_comments) \
                     + "\t" + str(quarantine) \
                     + "\t" + str(viewCount) \
                     + "\t" + str(url)   \
                     + "\t" + str(author) \
                     + "\t" + str(category) \
                     + "\t" + str(contest_mode) \
                     + "\t" + str(created_utc) \
                     + "\t" + str(crosspost_parent) \
                     + "\t" + str(discussion_type) \
                     + "\t" + str(distinguished) \
                     + "\t" + str(gilded) \
                     + "\t" + str(contest_mode) \
                     + "\t" + str(id) \
                     + "\t" + str(locked) \
                     + "\t" + str(contest_mode) \
                     + "\t" + str(no_follow) \
                     + "\t" + str(num_comments) \
                     + "\t" + str(num_crossposts) \
                     + "\t" + str(over_18) \
                     + "\t" + str(permalink) \
                     + "\t" + str(pwls) \
                     + "\t" + str(removal_reason) \
                     + "\t" + str(removed_by) \
                     + "\t" + str(removed_by_category) \
                     + "\t" + str(retrieved_on) \
                     + "\t" + str(score) \
                     + "\t" + str(selftext) \
                     + "\t" + str(subreddit_subscribers) \
                     + "\t" + str(total_awards_received) + "\n"

            fOut.write(outputLine)
            s+=1
    fOut.close()
    logging.info("processed <" + str(s) + "> entries")


def getSubmissionHeaderLine():
    headerLine = 'title' \
             + "\t" + "fullName" \
             + "\t" + "upvoteRatio" \
             + "\t" + "numComments" \
             + "\t" + "quarantine" \
             + "\t" + "viewcount" \
             + "\t" + "url"   \
             + "\t" + "author" \
             + "\t" + "category" \
             + "\t" + "contest_mode" \
             + "\t" + "created_utc" \
             + "\t" + "crosspost_parent" \
             + "\t" + "discussion_type" \
             + "\t" + "distinguished" \
             + "\t" + "gilded" \
             + "\t" + "contest_mode" \
             + "\t" + "id" \
             + "\t" + "locked" \
             + "\t" + "contest_mode" \
             + "\t" + "no_follow" \
             + "\t" + "num_comments" \
             + "\t" + "num_crossposts" \
             + "\t" + "over_18" \
             + "\t" + "permalink" \
             + "\t" + "pwls" \
             + "\t" + "removal_reason" \
             + "\t" + "removed_by" \
             + "\t" + "removed_by_category" \
             + "\t" + "retrieved_on" \
             + "\t" + "score" \
             + "\t" + "selftext" \
             + "\t" + "subreddit_subscribers" \
             + "\t" + "total_awards_received"+  "\n"
    return headerLine

def parseCommentFileList():

    fComments = open(commentsFileList, "r")
    commentsFiles = fComments.readlines()
    fComments .close()
    logging.info("read <" + str(len(commentsFiles)) + "> filenames")

    fullKeyList = []

    c=1
    for commentFile in commentsFiles:
        commentLines = []
        with open(commentFile.strip()) as fComment:
            commentLines = fComment.read().splitlines()

        results = []
        logging.info("reading <" + commentFile + ">")
        outputFolder = os.path.dirname(commentFile)
        outputFile = os.path.join(outputFolder, os.path.basename(commentFile).split(".")[0] + ".tsv")
        fOut= open(outputFile,"w+")
        fOut.write(getCommentHeaderLine())

        print(str(c))
        for commentLine in commentLines:
            result = json.loads(commentLine)
            keysList = list(result.keys())
            valuesList = list(result.values())
            #logging.info("found <" + str(len(keysList)) + "> keys")
            diff = list(set(keysList) - set(fullKeyList))
            if len(diff) > 0:
                logging.info("found <" + str(len(diff)) + "> new keys")
                logging.info(diff)
                fullKeyList.extend(diff)


            ### Author
            author = ""
            try:
                author = result['author']
            except:
                author = 'missing'

            ### category
            category = ""
            try:
                category = result['category']
            except:
                category = 'missing'

            ### contest_mode
            contest_mode = ""
            try:
                contest_mode = result['contest_mode']
            except:
                contest_mode = 'missing'

            ### created_utc
            created_utc = ""
            try:
                created_utc = result['created_utc']
            except:
                created_utc = 'missing'

            ### crosspost_parent
            crosspost_parent = ""
            try:
                crosspost_parent = result['crosspost_parent']
            except:
                crosspost_parent = 'missing'

            ### discussion_type
            discussion_type = ""
            try:
                discussion_type = result['discussion_type']
            except:
                discussion_type = 'missing'

            ### distinguished
            distinguished = ""
            try:
                distinguished = result['distinguished']
            except:
                distinguished = 'missing'

            ### gilded
            gilded = ""
            try:
                gilded = result['gilded']
            except:
                gilded = 'missing'

            ### contest_mode
            contest_mode = ""
            try:
                contest_mode = result['contest_mode']
            except:
                contest_mode = 'missing'

            ### id
            id = ""
            try:
                id = result['id']
            except:
                id = 'missing'

            ### linkid
            linkid = ""
            try:
                linkid = result['linkid']
            except:
                linkid = 'missing'

            ### locked
            locked = ""
            try:
                locked = result['locked']
            except:
                locked = 'missing'

            ### contest_mode
            contest_mode = ""
            try:
                contest_mode = result['contest_mode']
            except:
                contest_mode = 'missing'

            ### no_follow
            no_follow = ""
            try:
                no_follow = result['no_follow']
            except:
                no_follow = 'missing'

            ### num_comments
            num_comments = ""
            try:
                num_comments = result['num_comments']
            except:
                num_comments = 'missing'

            ### num_crossposts
            num_crossposts = ""
            try:
                num_crossposts = result['num_crossposts']
            except:
                num_crossposts = 'missing'

            ### over_18
            over_18 = ""
            try:
                over_18 = result['over_18']
            except:
                over_18 = 'missing'

            ### permalink
            permalink = ""
            try:
                permalink = result['permalink']
            except:
                permalink = 'missing'

            ### pwls
            pwls = ""
            try:
                pwls = result['pwls']
            except:
                pwls = 'pwls'

            ### quarantine
            quarantine = ""
            try:
                quarantine = result['quarantine']
            except:
                quarantine = 'missing'

            ### removal_reason
            removal_reason = ""
            try:
                removal_reason = result['removal_reason']
            except:
                removal_reason = 'missing'

            ### removed_by
            removed_by = ""
            try:
                removed_by = result['removed_by']
            except:
                removed_by = 'missing'

            ### removed_by_category
            removed_by_category = ""
            try:
                removed_by_category = result['removed_by_category']
            except:
                removed_by_category = 'missing'

            ### retrieved_on
            retrieved_on = ""
            try:
                retrieved_on = result['retrieved_on']
            except:
                retrieved_on = 'missing'

            ### score
            score = ""
            try:
                score = result['score']
            except:
                score = 'missing'

            ### selftext
            selftext = ""
            try:
                selftext = result['selftext']
            except:
                selftext = 'missing'

            ### subreddit_subscribers
            subreddit_subscribers = ""
            try:
                subreddit_subscribers = result['subreddit_subscribers']
            except:
                subreddit_subscribers = 'missing'

            ### url
            url = ""
            try:
                url = result['url']
            except:
                url = 'missing'

            ### total_awards_received
            total_awards_received = ""
            try:
                total_awards_received = result['total_awards_received']
            except:
                total_awards_received = 'missing'

            title = ""
            try:
                title = result['title']
            except:
                title = 'missing'

            fullName = ""
            try:
                fullName = result['author_fullname']
            except:
                fullName = 'missing'

            upvoteRatio = ""
            try:
                upvoteRatio = str(result['upvote_ratio'])
            except:
                upvoteRatio = 'missing'


            viewCount = ""
            try:
                viewCount = str(result['view_count'])
            except:
                viewCount = 'missing'

            outputLine = title \
                     + "\t" + str(fullName) \
                     + "\t" + str(upvoteRatio) \
                     + "\t" + str(num_comments) \
                     + "\t" + str(quarantine) \
                     + "\t" + str(viewCount) \
                     + "\t" + str(url)   \
                     + "\t" + str(author) \
                     + "\t" + str(category) \
                     + "\t" + str(contest_mode) \
                     + "\t" + str(created_utc) \
                     + "\t" + str(crosspost_parent) \
                     + "\t" + str(discussion_type) \
                     + "\t" + str(distinguished) \
                     + "\t" + str(gilded) \
                     + "\t" + str(contest_mode) \
                     + "\t" + str(id) \
                     + "\t" + str(linkid) \
                     + "\t" + str(locked) \
                     + "\t" + str(contest_mode) \
                     + "\t" + str(no_follow) \
                     + "\t" + str(num_comments) \
                     + "\t" + str(num_crossposts) \
                     + "\t" + str(over_18) \
                     + "\t" + str(permalink) \
                     + "\t" + str(pwls) \
                     + "\t" + str(removal_reason) \
                     + "\t" + str(removed_by) \
                     + "\t" + str(removed_by_category) \
                     + "\t" + str(retrieved_on) \
                     + "\t" + str(score) \
                     + "\t" + str(selftext) \
                     + "\t" + str(subreddit_subscribers) \
                     + "\t" + str(total_awards_received) + "\n"

            fOut.write(outputLine)
            c+=1
    fOut.close()
    logging.info("processed <" + str(c) + "> entries")


def getCommentHeaderLine():
    headerLine = 'title' \
             + "\t" + "fullName" \
             + "\t" + "upvoteRatio" \
             + "\t" + "numComments" \
             + "\t" + "quarantine" \
             + "\t" + "viewcount" \
             + "\t" + "url"   \
             + "\t" + "author" \
             + "\t" + "category" \
             + "\t" + "contest_mode" \
             + "\t" + "created_utc" \
             + "\t" + "crosspost_parent" \
             + "\t" + "discussion_type" \
             + "\t" + "distinguished" \
             + "\t" + "gilded" \
             + "\t" + "contest_mode" \
             + "\t" + "id" \
             + "\t" + "linkid" \
             + "\t" + "locked" \
             + "\t" + "contest_mode" \
             + "\t" + "no_follow" \
             + "\t" + "num_comments" \
             + "\t" + "num_crossposts" \
             + "\t" + "over_18" \
             + "\t" + "permalink" \
             + "\t" + "pwls" \
             + "\t" + "removal_reason" \
             + "\t" + "removed_by" \
             + "\t" + "removed_by_category" \
             + "\t" + "retrieved_on" \
             + "\t" + "score" \
             + "\t" + "selftext" \
             + "\t" + "subreddit_subscribers" \
             + "\t" + "total_awards_received"+  "\n"
    return headerLine


def main(argv=None): # IGNORE:C0111

    setlocale(LC_NUMERIC, 'no_NO')
    if argv is None:
        argv = sys.argv

    md5String = hashlib.md5(b"CBGAMGOUS").hexdigest()
    parseArgs(argv)
    initLogger(md5String)
    if submissionsFileList:
        parseSubmissionFileList()
    else:
        parseCommentFileList()



if __name__ == '__main__':

    sys.exit(main())

